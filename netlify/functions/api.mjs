import { createHash, pbkdf2Sync, randomBytes, randomUUID, timingSafeEqual } from 'node:crypto';
import { getStore } from '@netlify/blobs';
import { COURSE } from '../lib/course-data.mjs';
import { runSQL, equalResults } from '../lib/sql-engine.mjs';

const schema = {
  users: ['id', 'name', 'email', 'age', 'city'],
  products: ['id', 'name', 'price', 'category'],
  orders: ['id', 'user_id', 'total', 'created_at'],
  departments: ['id', 'name', 'city'],
  employees: ['id', 'name', 'department_id', 'manager_id', 'salary'],
  order_items: ['id', 'order_id', 'product_id', 'quantity'],
  reviews: ['id', 'user_id', 'product_id', 'rating', 'comment'],
  inventory: ['id', 'product_id', 'quantity', 'status'],
};

const sha = value => createHash('sha256').update(value).digest('hex');
const json = (value, status = 200, extra = {}) => Response.json(value, { status, headers: { 'cache-control': 'no-store', ...extra } });
const emailValid = value => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
const passwordHash = (password, salt = randomBytes(16).toString('hex')) =>
  `${salt}:${pbkdf2Sync(password, salt, 200000, 32, 'sha256').toString('hex')}`;
function verifyPassword(password, stored) {
  const [salt, digest] = stored.split(':');
  const actual = Buffer.from(passwordHash(password, salt).split(':')[1], 'hex');
  return timingSafeEqual(actual, Buffer.from(digest, 'hex'));
}
const publicCourse = COURSE.map(level => ({
  title: level.title, topic: level.topic, theory: level.theory, example: level.example,
  tasks: level.tasks.map(({ title, prompt, hint1, hint2, explanation, mode }) =>
    ({ title, prompt, hint1, hint2, explanation, mode })),
}));

class HttpError extends Error {
  constructor(status, message) { super(message); this.status = status; }
}

function explainMismatch(actual, expected, ordered, mode) {
  const sameColumns = JSON.stringify(actual.columns.map(x => x.toLowerCase())) ===
    JSON.stringify(expected.columns.map(x => x.toLowerCase()));
  if (!sameColumns) {
    return `Проверьте столбцы результата. Нужно: ${expected.columns.join(', ')}. Сейчас: ${actual.columns.join(', ')}.`;
  }
  if (actual.rows.length !== expected.rows.length) {
    if (mode === 'write') return 'Изменено не то количество строк. Проверьте условие WHERE и значения в SET или VALUES.';
    if (mode === 'schema') return 'Структура таблицы отличается: проверьте список столбцов и ограничений.';
    return `Ожидается ${expected.rows.length} строк, получено ${actual.rows.length}. Проверьте WHERE, JOIN, GROUP BY или LIMIT.`;
  }
  if (ordered && equalResults(actual, expected, false)) return 'Значения верны, но порядок строк отличается. Проверьте ORDER BY и направление ASC или DESC.';
  if (mode === 'write') return 'Строки изменены не так, как требуется. Проверьте значения в SET или VALUES и условие WHERE.';
  if (mode === 'schema') return 'Проверьте типы, PRIMARY KEY, NOT NULL и DEFAULT у каждого столбца.';
  return 'Число строк и столбцы совпали, но значения отличаются. Проверьте условия, вычисления и связи таблиц.';
}

function progress(account) {
  const solved = account.solved || [];
  const done = new Set(solved.map(x => `${x.level}:${x.task}`));
  let unlocked = 0;
  for (let i = 0; i < COURSE.length; i++) {
    if (COURSE[i].tasks.every((_, j) => done.has(`${i}:${j}`))) unlocked = i + 1;
    else break;
  }
  unlocked = Math.max(unlocked, ...solved.map(x => x.level), 0);
  return { solved, days: account.days || [], unlocked: Math.min(unlocked, COURSE.length - 1),
    xp: solved.length * 25, total: COURSE.reduce((n, x) => n + x.tasks.length, 0) };
}

function taskAt(level, task) {
  if (!Number.isInteger(level) || !Number.isInteger(task) || !COURSE[level]?.tasks[task]) {
    throw new HttpError(400, 'Задание не найдено.');
  }
  return COURSE[level].tasks[task];
}

function cookieValue(request, name) {
  const raw = request.headers.get('cookie') || '';
  return raw.split(';').map(x => x.trim()).find(x => x.startsWith(`${name}=`))?.slice(name.length + 1) || null;
}

async function readBody(request) {
  const raw = await request.text();
  if (raw.length > 10000) throw new HttpError(400, 'Слишком большой запрос.');
  try { return JSON.parse(raw || '{}'); }
  catch { throw new HttpError(400, 'Некорректный JSON.'); }
}

export function createHandler(stores = {}) {
  return async function handler(request) {
    try {
      const url = new URL(request.url);
      const path = url.searchParams.get('path') || url.pathname.replace(/^\/api\//, '');
      if (request.method === 'POST') {
        const origin = request.headers.get('origin');
        if (origin && origin !== url.origin) throw new HttpError(403, 'Запрос с другого сайта запрещён.');
      }
      const accounts = stores.accounts || getStore({ name: 'sql-studio-accounts', consistency: 'strong' });
      const sessions = stores.sessions || getStore({ name: 'sql-studio-sessions', consistency: 'strong' });
      const resets = stores.resets || getStore({ name: 'sql-studio-resets', consistency: 'strong' });

      async function current() {
        const token = cookieValue(request, 'session');
        if (!token) return null;
        const session = await sessions.get(sha(token), { type: 'json', consistency: 'strong' });
        if (!session || session.expires < Date.now()) return null;
        const account = await accounts.get(sha(session.email), { type: 'json', consistency: 'strong' });
        return account ? { account, key: sha(session.email) } : null;
      }
      async function requireUser() {
        const user = await current();
        if (!user) throw new HttpError(403, 'Войдите в аккаунт, чтобы сохранить прогресс.');
        return user;
      }

      if (request.method === 'GET' && path === 'bootstrap') {
        const user = await current();
        return json({ user: user ? { id: user.account.id, name: user.account.name, email: user.account.email } : null,
          course: publicCourse, progress: user ? progress(user.account) : null, schema });
      }
      if (request.method !== 'POST') throw new HttpError(404, 'Адрес не найден.');
      const body = await readBody(request);

      if (path === 'register' || path === 'login') {
        const email = String(body.email || '').trim().toLowerCase();
        const password = String(body.password || '');
        if (!emailValid(email) || password.length < 8 || password.length > 200) {
          throw new HttpError(400, 'Укажите корректный email и пароль от 8 до 200 символов.');
        }
        const key = sha(email);
        if (path === 'register') {
          const name = String(body.name || '').trim().slice(0, 60);
          if (!name) throw new HttpError(400, 'Введите имя.');
          const created = await accounts.setJSON(key, { id: randomUUID(), email, name,
            password: passwordHash(password), solved: [], days: [] }, { onlyIfNew: true });
          if (!created.modified) throw new HttpError(400, 'Этот email уже зарегистрирован.');
        }
        const account = await accounts.get(key, { type: 'json', consistency: 'strong' });
        if (!account || !verifyPassword(password, account.password)) {
          throw new HttpError(400, 'Неверный email или пароль.');
        }
        const token = randomBytes(32).toString('base64url');
        await sessions.setJSON(sha(token), { email, expires: Date.now() + 30 * 86400000 });
        return json({ ok: true }, 200, { 'set-cookie': `session=${token}; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=2592000` });
      }
      if (path === 'logout') {
        const token = cookieValue(request, 'session');
        if (token) await sessions.delete(sha(token));
        return json({ ok: true }, 200, { 'set-cookie': 'session=; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=0' });
      }
      if (path === 'forgot') {
        const email = String(body.email || '').trim().toLowerCase();
        if (!process.env.SMTP_HOST) throw new HttpError(503, 'Восстановление пароля по почте пока не настроено.');
        const account = await accounts.get(sha(email), { type: 'json', consistency: 'strong' });
        if (account) {
          const token = randomBytes(32).toString('base64url');
          await resets.setJSON(sha(token), { email, expires: Date.now() + 30 * 60000 });
          const { default: nodemailer } = await import('nodemailer');
          const transport = nodemailer.createTransport({ host: process.env.SMTP_HOST,
            port: Number(process.env.SMTP_PORT || 587), secure: Number(process.env.SMTP_PORT || 587) === 465,
            auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASSWORD } });
          await transport.sendMail({ from: process.env.SMTP_FROM, to: email, subject: 'Сброс пароля SQL Studio',
            text: `Откройте ссылку (действует 30 минут):\n${url.origin}/?reset=${token}` });
        }
        return json({ ok: true, message: 'Если адрес зарегистрирован, письмо отправлено.' });
      }
      if (path === 'reset') {
        const token = String(body.token || '');
        const password = String(body.password || '');
        if (password.length < 8 || password.length > 200) throw new HttpError(400, 'Пароль должен содержать от 8 до 200 символов.');
        const item = await resets.get(sha(token), { type: 'json', consistency: 'strong' });
        if (!item || item.expires < Date.now()) throw new HttpError(400, 'Ссылка недействительна или срок её действия истёк.');
        const key = sha(item.email);
        const entry = await accounts.getWithMetadata(key, { type: 'json', consistency: 'strong' });
        if (!entry) throw new HttpError(400, 'Аккаунт не найден.');
        entry.data.password = passwordHash(password);
        const changed = await accounts.setJSON(key, entry.data, { onlyIfMatch: entry.etag });
        if (!changed.modified) throw new HttpError(409, 'Повторите попытку. Данные аккаунта изменились.');
        await resets.delete(sha(token));
        return json({ ok: true });
      }
      if (path === 'solution') {
        const user = await requireUser();
        const level = Number(body.level), task = Number(body.task);
        const item = taskAt(level, task);
        if (level > progress(user.account).unlocked) throw new HttpError(403, 'Сначала завершите предыдущий уровень.');
        return json({ solution: item.solution });
      }
      if (path === 'run' || path === 'check') {
        const level = Number(body.level), task = Number(body.task);
        const item = taskAt(level, task);
        const user = path === 'check' || item.mode !== 'read' ? await requireUser() : await current();
        if (user && level > progress(user.account).unlocked) throw new HttpError(403, 'Сначала завершите предыдущий уровень.');
        if (path === 'check' && task > 0 && !(user.account.solved || []).some(x => x.level === level && x.task === task - 1)) {
          throw new HttpError(403, 'Сначала выполните предыдущее задание.');
        }
        const query = body.query;
        const result = await runSQL(query, item.mode, item.target);
        if (path === 'run') return json({ result });
        const expected = await runSQL(item.solution, item.mode, item.target);
        let correct = equalResults(result, expected, level === 2 || (level === 14 && task === 5));
        const required = item.required || (task === COURSE[level].tasks.length - 1 ? COURSE[level].required : null);
        let message = correct ? item.explanation : explainMismatch(result, expected, level === 2 || (level === 14 && task === 5), item.mode);
        if (correct && required && !new RegExp(`\\b${required}\\b`, 'i').test(query)) {
          correct = false;
          message = `Результат совпал, но нужно использовать ${required}.`;
        }
        let account = user.account;
        if (correct && !(account.solved || []).some(x => x.level === level && x.task === task)) {
          for (let attempt = 0; attempt < 4; attempt++) {
            const entry = await accounts.getWithMetadata(user.key, { type: 'json', consistency: 'strong' });
            if (!entry) throw new HttpError(403, 'Аккаунт не найден.');
            account = entry.data;
            if ((account.solved || []).some(x => x.level === level && x.task === task)) break;
            account.solved ||= [];
            account.days ||= [];
            account.solved.push({ level, task, hints: Math.max(0, Math.min(3, Number(body.hints) || 0)), solved_at: Math.floor(Date.now() / 1000) });
            const day = new Date().toISOString().slice(0, 10);
            if (!account.days.includes(day)) account.days.unshift(day);
            const saved = await accounts.setJSON(user.key, account, { onlyIfMatch: entry.etag });
            if (saved.modified) break;
            if (attempt === 3) throw new HttpError(409, 'Не удалось сохранить прогресс. Повторите проверку.');
          }
        }
        return json({ correct, message, result, progress: progress(account) });
      }
      throw new HttpError(404, 'Адрес не найден.');
    } catch (error) {
      const message = error?.message || '';
      const status = error?.status || (/^(Ошибка SQL|В этом|Введите|Создайте|Результат|Выполняйте|Столбец|Таблица)/.test(message) ? 400 : 500);
      if (status >= 500) console.error(error);
      return json({ error: status >= 500 ? 'Внутренняя ошибка сервера. Попробуйте позже.' : message }, status);
    }
  };
}

export default createHandler();

export const config = { path: '/api/:action' };
