import initSqlJs from 'sql.js/dist/sql-asm.js';
import { SCHEMA_SQL } from './course-data.mjs';

let sqlPromise;
const engine = () => (sqlPromise ??= initSqlJs());

function singleStatement(query) {
  if (typeof query !== 'string' || !query.trim() || query.length > 3000) {
    throw new Error('Введите запрос длиной до 3000 символов.');
  }
  const trimmed = query.trim();
  const withoutFinal = trimmed.endsWith(';') ? trimmed.slice(0, -1) : trimmed;
  if (withoutFinal.includes(';') || /--|\/\*|\*\//.test(withoutFinal)) {
    throw new Error('Выполняйте только один запрос без комментариев.');
  }
  return withoutFinal;
}

function validate(query, mode, target) {
  if (mode === 'read') {
    if (!/^(SELECT|WITH)\b/i.test(query) || /\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|PRAGMA|ATTACH|DETACH|REPLACE|VACUUM|RECURSIVE)\b/i.test(query)) {
      throw new Error('В этом задании разрешены только запросы на чтение SELECT и WITH.');
    }
  } else if (mode === 'write') {
    if (target !== 'inventory' || !/^(?:INSERT\s+INTO|UPDATE|DELETE\s+FROM)\s+inventory\b/i.test(query)) {
      throw new Error('В этом задании изменяйте только таблицу inventory.');
    }
  } else if (mode === 'schema') {
    if (target !== 'sandbox_table' || !/^CREATE\s+TABLE\s+sandbox_table\b/i.test(query)) {
      throw new Error('Создайте только таблицу sandbox_table.');
    }
  } else {
    throw new Error('Неизвестный режим задания.');
  }
}

function queryRows(db, sql) {
  const statement = db.prepare(sql);
  try {
    const columns = statement.getColumnNames();
    const rows = [];
    while (statement.step()) {
      if (rows.length >= 100) throw new Error('Результат слишком большой. Добавьте LIMIT (максимум 100 строк).');
      rows.push(statement.get());
    }
    return { columns, rows };
  } finally {
    statement.free();
  }
}

export async function runSQL(input, mode = 'read', target = null) {
  const query = singleStatement(input);
  validate(query, mode, target);
  const SQL = await engine();
  const db = new SQL.Database();
  try {
    db.run(SCHEMA_SQL);
    const result = queryRows(db, query);
    if (mode === 'write') return queryRows(db, 'SELECT * FROM inventory ORDER BY id');
    if (mode === 'schema') return queryRows(db, 'PRAGMA table_info(sandbox_table)');
    return result;
  } catch (error) {
    const message = String(error?.message || error);
    if (/no such table/i.test(message)) throw new Error('Таблица не найдена. Проверьте её имя в схеме данных.');
    if (/no such column/i.test(message)) throw new Error('Столбец не найден. Проверьте его имя в схеме данных.');
    if (/near "FORM"/i.test(message)) throw new Error('Возможно, вы имели в виду FROM. Проверьте написание команды.');
    if (error instanceof Error && !/^(?:Ошибка SQL|Введите|Выполняйте|В этом|Создайте|Результат|Неизвестный)/.test(message)) {
      throw new Error(`Ошибка SQL: ${message}`);
    }
    throw error;
  } finally {
    db.close();
  }
}

export function equalResults(actual, expected, ordered = false) {
  if (JSON.stringify(actual.columns.map(x => x.toLowerCase())) !== JSON.stringify(expected.columns.map(x => x.toLowerCase()))) return false;
  if (ordered) return JSON.stringify(actual.rows) === JSON.stringify(expected.rows);
  const sorted = rows => rows.map(row => JSON.stringify(row)).sort();
  return JSON.stringify(sorted(actual.rows)) === JSON.stringify(sorted(expected.rows));
}
