import test from 'node:test';
import assert from 'node:assert/strict';
import { COURSE } from '../lib/course-data.mjs';
import { runSQL } from '../lib/sql-engine.mjs';
import { createHandler } from '../functions/api.mjs';
import { readFileSync } from 'node:fs';
import { runInNewContext } from 'node:vm';

class MemoryStore {
  values = new Map();
  version = 0;
  async get(key) { return structuredClone(this.values.get(key)?.data ?? null); }
  async getWithMetadata(key) {
    const item = this.values.get(key);
    return item ? { data: structuredClone(item.data), etag: item.etag } : null;
  }
  async setJSON(key, value, options = {}) {
    const old = this.values.get(key);
    if (options.onlyIfNew && old) return { modified: false };
    if (options.onlyIfMatch && old?.etag !== options.onlyIfMatch) return { modified: false };
    const etag = `"${++this.version}"`;
    this.values.set(key, { data: structuredClone(value), etag });
    return { modified: true, etag };
  }
  async delete(key) { this.values.delete(key); }
}

test('all 100 course solutions execute in isolated SQLite', async () => {
  assert.equal(COURSE.length, 15);
  assert.equal(COURSE.reduce((n, level) => n + level.tasks.length, 0), 100);
  for (const level of COURSE) {
    for (const task of level.tasks) {
      const result = await runSQL(task.solution, task.mode, task.target);
      assert.ok(result.columns.length, `${level.title}: ${task.title}`);
    }
  }
  await assert.rejects(runSQL('DROP TABLE users'));
  await assert.rejects(runSQL('SELECT * FROM users; DELETE FROM users'));
  await runSQL(COURSE[12].tasks[0].solution, 'write', 'inventory');
  assert.deepEqual((await runSQL('SELECT id FROM inventory WHERE id=5')).rows, []);
});

test('register, session, lock, grading and persisted progress', async () => {
  const handler = createHandler({ accounts: new MemoryStore(), sessions: new MemoryStore(), resets: new MemoryStore() });
  let cookie = '';
  async function api(path, body) {
    const request = new Request(`https://example.netlify.app/api/${path}`, {
      method: body ? 'POST' : 'GET',
      headers: { 'content-type': 'application/json', cookie },
      body: body ? JSON.stringify(body) : undefined,
    });
    const response = await handler(request);
    if (response.headers.get('set-cookie')) cookie = response.headers.get('set-cookie').split(';', 1)[0];
    return { status: response.status, data: await response.json() };
  }
  const anon = await api('bootstrap');
  assert.equal(anon.status, 200);
  assert.equal(anon.data.user, null);
  assert.equal(anon.data.course[0].tasks[0].solution, undefined);
  assert.equal((await api('register', { name: 'Тест', email: 'test@example.com', password: 'password123' })).status, 200);
  assert.equal((await api('check', { level: 1, task: 0, query: COURSE[1].tasks[0].solution })).status, 403);
  const wrongColumns = await api('check', { level: 0, task: 0, query: 'SELECT age FROM users' });
  assert.equal(wrongColumns.data.correct, false);
  assert.match(wrongColumns.data.message, /Нужно: name/);
  const wrongCount = await api('check', { level: 0, task: 0, query: 'SELECT name FROM users LIMIT 1' });
  assert.equal(wrongCount.data.correct, false);
  assert.match(wrongCount.data.message, /Ожидается 5 строк, получено 1/);
  assert.equal((await api('check', { level: 0, task: 0, query: COURSE[0].tasks[0].solution })).data.correct, true);
  for (let task = 1; task < COURSE[0].tasks.length; task++) {
    assert.equal((await api('check', { level: 0, task, query: COURSE[0].tasks[task].solution })).data.correct, true);
  }
  const state = await api('bootstrap');
  assert.equal(state.data.progress.solved.length, COURSE[0].tasks.length);
  assert.equal(state.data.progress.xp, COURSE[0].tasks.length * 25);
  assert.equal(state.data.progress.unlocked, 1);
  assert.equal((await api('logout', {})).status, 200);
  assert.equal((await api('bootstrap')).data.user, null);
});

test('every exercise has distinct teaching material before practice', () => {
  const window = {};
  runInNewContext(readFileSync(new URL('../../task-lessons.js', import.meta.url), 'utf8'), { window });
  assert.equal(window.TASK_LESSONS.length, COURSE.length);
  let count = 0;
  for (let level = 0; level < COURSE.length; level++) {
    assert.equal(window.TASK_LESSONS[level].length, COURSE[level].tasks.length, COURSE[level].title);
    for (let task = 0; task < COURSE[level].tasks.length; task++) {
      const teaching = window.TASK_LESSONS[level][task];
      assert.equal(teaching.length, 3, `${level + 1}.${task + 1}`);
      for (let part = 0; part < teaching.length; part++) {
        assert.ok(teaching[part].length >= (part === 2 ? 25 : 45), `${level + 1}.${task + 1}: missing explanation`);
      }
      count++;
    }
  }
  assert.equal(count, 100);
});

test('all 100 published solutions pass the real progress checks', async () => {
  const handler = createHandler({ accounts: new MemoryStore(), sessions: new MemoryStore(), resets: new MemoryStore() });
  let cookie = '';
  async function api(path, body) {
    const response = await handler(new Request(`https://example.netlify.app/api/${path}`, {
      method: 'POST', headers: { 'content-type': 'application/json', cookie }, body: JSON.stringify(body),
    }));
    if (response.headers.get('set-cookie')) cookie = response.headers.get('set-cookie').split(';', 1)[0];
    return { status: response.status, data: await response.json() };
  }
  assert.equal((await api('register', { name: 'Курс', email: 'course@example.com', password: 'password123' })).status, 200);
  for (let level = 0; level < COURSE.length; level++) {
    for (let task = 0; task < COURSE[level].tasks.length; task++) {
      const item = COURSE[level].tasks[task];
      const response = await api('check', { level, task, query: item.solution });
      assert.equal(response.status, 200, `${level + 1}.${task + 1} ${item.title}: ${response.data.error}`);
      assert.equal(response.data.correct, true, `${level + 1}.${task + 1} ${item.title}: ${response.data.message}`);
    }
  }
  const screenshotQuery = await api('check', {
    level: 0, task: 6, query: 'SELECT name, price * 2 AS double_price\nFROM products',
  });
  assert.equal(screenshotQuery.data.correct, true, 'The query shown in the user screenshot must pass');
  const state = await handler(new Request('https://example.netlify.app/api/bootstrap', { headers: { cookie } }));
  const data = await state.json();
  assert.equal(data.progress.solved.length, 100);
  assert.equal(data.progress.unlocked, COURSE.length - 1);
});
