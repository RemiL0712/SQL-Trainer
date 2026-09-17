import test from 'node:test';
import assert from 'node:assert/strict';
import { COURSE } from '../lib/course-data.mjs';
import { runSQL } from '../lib/sql-engine.mjs';
import { createHandler } from '../functions/api.mjs';

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
  assert.equal((await api('check', { level: 0, task: 0, query: 'SELECT age FROM users' })).data.correct, false);
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
