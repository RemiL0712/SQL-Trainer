"""Local SQL learning server. Run with: python server.py"""
import hashlib
import hmac
import json
import os
import re
import secrets
import smtplib
import sqlite3
import time
from email.message import EmailMessage
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from content import LEVELS, SCHEMA

ROOT = Path(__file__).resolve().parent
DB = Path(os.environ.get("DB_PATH", str(ROOT / "progress.sqlite3")))
SESSIONS = {}
MAX_QUERY = 3000


class ClosingConnection(sqlite3.Connection):
    def __exit__(self, exc_type, exc_value, traceback):
        try:
            return super().__exit__(exc_type, exc_value, traceback)
        finally:
            self.close()


def connect():
    db = sqlite3.connect(DB, factory=ClosingConnection)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    return db


def init_db():
    DB.parent.mkdir(parents=True, exist_ok=True)
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS accounts(id INTEGER PRIMARY KEY, name TEXT NOT NULL,
          email TEXT NOT NULL UNIQUE, password TEXT NOT NULL, created_at INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS solved(user_id INTEGER NOT NULL, level INTEGER NOT NULL,
          task INTEGER NOT NULL, hints INTEGER NOT NULL DEFAULT 0, solved_at INTEGER NOT NULL,
          PRIMARY KEY(user_id,level,task), FOREIGN KEY(user_id) REFERENCES accounts(id));
        CREATE TABLE IF NOT EXISTS activity(user_id INTEGER NOT NULL, day TEXT NOT NULL,
          PRIMARY KEY(user_id,day), FOREIGN KEY(user_id) REFERENCES accounts(id));
        CREATE TABLE IF NOT EXISTS resets(token_hash TEXT PRIMARY KEY, user_id INTEGER NOT NULL,
          expires INTEGER NOT NULL, FOREIGN KEY(user_id) REFERENCES accounts(id));
        CREATE TABLE IF NOT EXISTS legacy_unlocks(user_id INTEGER PRIMARY KEY, unlocked INTEGER NOT NULL,
          FOREIGN KEY(user_id) REFERENCES accounts(id));
        CREATE TABLE IF NOT EXISTS migrations(name TEXT PRIMARY KEY);
        """)
        if not db.execute("SELECT 1 FROM migrations WHERE name='expanded_course_v1'").fetchone():
            for account in db.execute("SELECT id FROM accounts").fetchall():
                solved = {(r[0], r[1]) for r in db.execute("SELECT level,task FROM solved WHERE user_id=?", (account["id"],))}
                old_unlocked = 0
                for level in range(10):
                    if (level, 0) in solved and (level, 1) in solved:
                        old_unlocked = level + 1
                    else:
                        break
                db.execute("INSERT INTO legacy_unlocks(user_id,unlocked) VALUES(?,?)", (account["id"], old_unlocked))
            db.execute("INSERT INTO migrations(name) VALUES('expanded_course_v1')")


def password_hash(password, salt=None):
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200000)
    return salt.hex() + ":" + digest.hex()


def check_password(password, stored):
    salt, digest = stored.split(":")
    return hmac.compare_digest(password_hash(password, bytes.fromhex(salt)).split(":")[1], digest)


def sandbox(query, mode="read", target=None):
    if not isinstance(query, str) or not query.strip() or len(query) > MAX_QUERY:
        raise ValueError("Введите запрос длиной до 3000 символов.")
    # SQLite's authorizer is the actual boundary; this early check gives a useful message.
    beginnings = r"SELECT|WITH" if mode == "read" else r"INSERT|UPDATE|DELETE|WITH|CREATE"
    if not re.match(r"^\s*(?:" + beginnings + r")\b", query, re.I):
        raise ValueError("Команда не подходит для этого задания.")
    db = sqlite3.connect(":memory:")
    try:
        db.executescript(SCHEMA)
        allowed = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION,
                   sqlite3.SQLITE_RECURSIVE}
        if mode == "write":
            allowed.update({sqlite3.SQLITE_INSERT, sqlite3.SQLITE_UPDATE, sqlite3.SQLITE_DELETE,
                            sqlite3.SQLITE_TRANSACTION})
        if mode == "schema":
            allowed.update({sqlite3.SQLITE_CREATE_TABLE, sqlite3.SQLITE_INSERT,
                            sqlite3.SQLITE_UPDATE, sqlite3.SQLITE_TRANSACTION,
                            sqlite3.SQLITE_PRAGMA, sqlite3.SQLITE_CREATE_INDEX})
        def authorize(action, a, b, c, d):
            if action not in allowed:
                return sqlite3.SQLITE_DENY
            if mode == "write" and action in (sqlite3.SQLITE_INSERT, sqlite3.SQLITE_UPDATE, sqlite3.SQLITE_DELETE) and a != target:
                return sqlite3.SQLITE_DENY
            if mode == "schema" and action == sqlite3.SQLITE_CREATE_TABLE and a != target:
                return sqlite3.SQLITE_DENY
            return sqlite3.SQLITE_OK
        db.set_authorizer(authorize)
        start = time.monotonic()
        db.set_progress_handler(lambda: 1 if time.monotonic() - start > 0.4 else 0, 1000)
        cursor = db.execute(query)
        if mode == "write":
            cursor = db.execute(f'SELECT * FROM "{target}" ORDER BY id')
        elif mode == "schema":
            cursor = db.execute(f'PRAGMA table_info("{target}")')
        columns = [item[0] for item in cursor.description or []]
        rows = cursor.fetchmany(101)
        if len(rows) > 100:
            raise ValueError("Результат слишком большой. Добавьте LIMIT (максимум 100 строк).")
        return {"columns": columns, "rows": [list(row) for row in rows]}
    except sqlite3.Error as exc:
        msg = str(exc)
        if "interrupted" in msg:
            raise ValueError("Запрос выполняется слишком долго. Упростите его.") from exc
        if "not authorized" in msg or "access to" in msg:
            raise ValueError("В этом задании разрешена только указанная операция над учебной таблицей.") from exc
        if "no such table" in msg:
            raise ValueError("Таблица не найдена. Проверьте её имя в схеме данных.") from exc
        if "no such column" in msg:
            raise ValueError("Столбец не найден. Проверьте его имя в схеме данных.") from exc
        if 'near "FORM"' in msg:
            raise ValueError("Возможно, вы имели в виду FROM. Проверьте написание команды.") from exc
        raise ValueError("Ошибка SQL: " + msg) from exc
    finally:
        db.close()


def equal_results(actual, expected, ordered=False):
    if [c.lower() for c in actual["columns"]] != [c.lower() for c in expected["columns"]]:
        return False
    if ordered:
        return actual["rows"] == expected["rows"]
    return sorted(map(repr, actual["rows"])) == sorted(map(repr, expected["rows"]))


def explain_mismatch(actual, expected, ordered=False, mode="read"):
    if [c.lower() for c in actual["columns"]] != [c.lower() for c in expected["columns"]]:
        return f"Проверьте столбцы результата. Нужно: {', '.join(expected['columns'])}. Сейчас: {', '.join(actual['columns'])}."
    if len(actual["rows"]) != len(expected["rows"]):
        if mode == "write":
            return "Изменено не то количество строк. Проверьте WHERE и значения в SET или VALUES."
        if mode == "schema":
            return "Структура таблицы отличается: проверьте список столбцов и ограничений."
        return f"Ожидается {len(expected['rows'])} строк, получено {len(actual['rows'])}. Проверьте WHERE, JOIN, GROUP BY или LIMIT."
    if ordered and equal_results(actual, expected):
        return "Значения верны, но порядок строк отличается. Проверьте ORDER BY и направление ASC или DESC."
    if mode == "write":
        return "Строки изменены не так, как требуется. Проверьте значения в SET или VALUES и условие WHERE."
    if mode == "schema":
        return "Проверьте типы, PRIMARY KEY, NOT NULL и DEFAULT у каждого столбца."
    return "Число строк и столбцы совпали, но значения отличаются. Проверьте условия, вычисления и связи таблиц."


def course():
    return [{"title": x["title"], "topic": x["topic"], "theory": x["theory"],
             "example": x["example"], "tasks": [{"title": t[0], "prompt": t[1],
             "hint1": t[3], "hint2": t[4], "explanation": t[6],
             "mode": t[7].get("mode", "read") if len(t) > 7 else "read"} for t in x["tasks"]]}
            for x in LEVELS]


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print("%s - %s" % (self.address_string(), format % args))

    def respond(self, data, status=200, cookie=None):
        payload = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(payload)

    def body(self):
        size = int(self.headers.get("Content-Length", "0"))
        if size > 10000:
            raise ValueError("Слишком большой запрос.")
        return json.loads(self.rfile.read(size) or b"{}")

    def current_user(self):
        cookie = SimpleCookie()
        try:
            cookie.load(self.headers.get("Cookie", ""))
            token = cookie["session"].value
        except (KeyError, Exception):
            return None
        record = SESSIONS.get(token)
        if not record or record[1] < time.time():
            return None
        with connect() as db:
            row = db.execute("SELECT id,name,email FROM accounts WHERE id=?", (record[0],)).fetchone()
        return dict(row) if row else None

    def require_user(self):
        user = self.current_user()
        if not user:
            raise PermissionError("Войдите в аккаунт, чтобы сохранить прогресс.")
        return user

    def progress(self, user_id):
        with connect() as db:
            solved = [dict(r) for r in db.execute("SELECT level,task,hints,solved_at FROM solved WHERE user_id=?", (user_id,))]
            days = [r[0] for r in db.execute("SELECT day FROM activity WHERE user_id=? ORDER BY day DESC", (user_id,))]
            legacy = db.execute("SELECT unlocked FROM legacy_unlocks WHERE user_id=?", (user_id,)).fetchone()
        unlocked = 0
        for i, level in enumerate(LEVELS):
            if all(any(s["level"] == i and s["task"] == j for s in solved) for j in range(len(level["tasks"]))):
                unlocked = i + 1
            else:
                break
        unlocked = max(unlocked, legacy["unlocked"] if legacy else 0, max((s["level"] for s in solved), default=0))
        return {"solved": solved, "days": days, "unlocked": min(unlocked, len(LEVELS) - 1),
                "xp": len(solved) * 25, "total": sum(len(l["tasks"]) for l in LEVELS)}

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/bootstrap":
            user = self.current_user()
            return self.respond({"user": user, "course": course(), "progress": self.progress(user["id"]) if user else None,
                                 "schema": {"users": ["id", "name", "email", "age", "city"],
                                            "products": ["id", "name", "price", "category"],
                                            "orders": ["id", "user_id", "total", "created_at"],
                                            "departments": ["id", "name", "city"],
                                            "employees": ["id", "name", "department_id", "manager_id", "salary"],
                                            "order_items": ["id", "order_id", "product_id", "quantity"],
                                            "reviews": ["id", "user_id", "product_id", "rating", "comment"],
                                            "inventory": ["id", "product_id", "quantity", "status"]}})
        path = path.lstrip("/") or "index.html"
        if path == "favicon.ico":
            path = "favicon.svg"
        if path not in ("index.html", "style.css", "app.js", "favicon.svg"):
            return self.send_error(404)
        data = (ROOT / path).read_bytes()
        kinds = {"html": "text/html", "css": "text/css", "js": "text/javascript", "svg": "image/svg+xml"}
        self.send_response(200)
        self.send_header("Content-Type", kinds[path.rsplit(".", 1)[1]] + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        try:
            path = urlparse(self.path).path
            data = self.body()
            if path == "/api/forgot":
                email = str(data.get("email", "")).strip().lower()
                with connect() as db:
                    row = db.execute("SELECT id FROM accounts WHERE email=?", (email,)).fetchone()
                    if row and os.environ.get("SMTP_HOST"):
                        token = secrets.token_urlsafe(32)
                        db.execute("INSERT INTO resets(token_hash,user_id,expires) VALUES(?,?,?)",
                                   (hashlib.sha256(token.encode()).hexdigest(), row["id"], int(time.time())+1800))
                        msg = EmailMessage()
                        msg["Subject"] = "Сброс пароля SQL Studio"
                        msg["From"] = os.environ["SMTP_FROM"]
                        msg["To"] = email
                        base_url = os.environ.get("PUBLIC_URL", f"http://127.0.0.1:{os.environ.get('PORT','8000')}").rstrip("/")
                        msg.set_content(f"Откройте ссылку для смены пароля (действует 30 минут):\n{base_url}/?reset={token}")
                        with smtplib.SMTP(os.environ["SMTP_HOST"], int(os.environ.get("SMTP_PORT", "587")), timeout=10) as smtp:
                            smtp.starttls()
                            smtp.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
                            smtp.send_message(msg)
                return self.respond({"ok": True, "message": "Если адрес зарегистрирован, письмо отправлено."})
            if path == "/api/reset":
                token = str(data.get("token", ""))
                password = str(data.get("password", ""))
                if len(password) < 8:
                    raise ValueError("Пароль должен содержать минимум 8 символов.")
                digest = hashlib.sha256(token.encode()).hexdigest()
                with connect() as db:
                    row = db.execute("SELECT user_id FROM resets WHERE token_hash=? AND expires>?", (digest,int(time.time()))).fetchone()
                    if not row:
                        raise ValueError("Ссылка недействительна или срок её действия истёк.")
                    db.execute("UPDATE accounts SET password=? WHERE id=?", (password_hash(password),row["user_id"]))
                    db.execute("DELETE FROM resets WHERE user_id=?", (row["user_id"],))
                return self.respond({"ok": True})
            if path in ("/api/register", "/api/login"):
                email = str(data.get("email", "")).strip().lower()
                password = str(data.get("password", ""))
                if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email) or len(password) < 8:
                    raise ValueError("Укажите корректный email и пароль от 8 символов.")
                with connect() as db:
                    if path.endswith("register"):
                        name = str(data.get("name", "")).strip()[:60]
                        if not name:
                            raise ValueError("Введите имя.")
                        try:
                            db.execute("INSERT INTO accounts(name,email,password,created_at) VALUES(?,?,?,?)",
                                       (name, email, password_hash(password), int(time.time())))
                        except sqlite3.IntegrityError:
                            raise ValueError("Этот email уже зарегистрирован.") from None
                    row = db.execute("SELECT * FROM accounts WHERE email=?", (email,)).fetchone()
                if not row or not check_password(password, row["password"]):
                    raise ValueError("Неверный email или пароль.")
                token = secrets.token_urlsafe(32)
                SESSIONS[token] = (row["id"], time.time() + 30 * 86400)
                secure = "; Secure" if os.environ.get("PUBLIC_URL", "").startswith("https://") else ""
                return self.respond({"ok": True}, cookie=f"session={token}; HttpOnly; SameSite=Lax; Path=/; Max-Age=2592000{secure}")
            if path == "/api/logout":
                cookie = SimpleCookie()
                cookie.load(self.headers.get("Cookie", ""))
                if "session" in cookie:
                    SESSIONS.pop(cookie["session"].value, None)
                return self.respond({"ok": True}, cookie="session=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0")
            if path == "/api/run":
                mode, target = "read", None
                if "level" in data and "task" in data:
                    level, task = int(data["level"]), int(data["task"])
                    if 0 <= level < len(LEVELS) and 0 <= task < len(LEVELS[level]["tasks"]):
                        meta = LEVELS[level]["tasks"][task][7] if len(LEVELS[level]["tasks"][task]) > 7 else {}
                        mode, target = meta.get("mode", "read"), meta.get("target")
                        if mode != "read":
                            user = self.require_user()
                            if level > self.progress(user["id"])["unlocked"]:
                                raise PermissionError("Сначала завершите предыдущий уровень.")
                result = sandbox(data.get("query", ""), mode, target)
                return self.respond({"result": result})
            if path == "/api/solution":
                self.require_user()
                level, task = int(data.get("level", -1)), int(data.get("task", -1))
                if not (0 <= level < len(LEVELS) and 0 <= task < len(LEVELS[level]["tasks"])):
                    raise ValueError("Задание не найдено.")
                return self.respond({"solution": LEVELS[level]["tasks"][task][5]})
            if path == "/api/check":
                user = self.require_user()
                level, task = int(data.get("level", -1)), int(data.get("task", -1))
                if not (0 <= level < len(LEVELS) and 0 <= task < len(LEVELS[level]["tasks"])):
                    raise ValueError("Задание не найдено.")
                state = self.progress(user["id"])
                if level > state["unlocked"]:
                    raise PermissionError("Сначала завершите предыдущий уровень.")
                if task and not any(s["level"] == level and s["task"] == task - 1 for s in state["solved"]):
                    raise PermissionError("Сначала выполните предыдущее задание.")
                query = data.get("query", "")
                item = LEVELS[level]["tasks"][task]
                meta = item[7] if len(item) > 7 else {}
                mode, target = meta.get("mode", "read"), meta.get("target")
                result = sandbox(query, mode, target)
                expected = sandbox(item[2], mode, target)
                correct = equal_results(result, expected, meta.get("ordered", level == 2 or (level == 14 and task == 5)))
                required = meta.get("required") or (LEVELS[level].get("required") if task == len(LEVELS[level]["tasks"]) - 1 else None)
                if correct and required and not re.search(r"\b" + required + r"\b", query, re.I):
                    correct = False
                    message = f"Результат совпал, но в финальном задании нужно использовать {required}."
                else:
                    message = item[6] if correct else explain_mismatch(result, expected, meta.get("ordered", level == 2 or (level == 14 and task == 5)), mode)
                if correct:
                    with connect() as db:
                        db.execute("INSERT OR IGNORE INTO solved(user_id,level,task,hints,solved_at) VALUES(?,?,?,?,?)",
                                   (user["id"], level, task, min(int(data.get("hints", 0)), 3), int(time.time())))
                        db.execute("INSERT OR IGNORE INTO activity(user_id,day) VALUES(?,date('now'))", (user["id"],))
                return self.respond({"correct": correct, "message": message, "result": result,
                                     "progress": self.progress(user["id"])})
            self.send_error(404)
        except PermissionError as exc:
            self.respond({"error": str(exc)}, 403)
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            self.respond({"error": str(exc)}, 400)


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", "8000"))
    host = os.environ.get("HOST", "127.0.0.1")
    print(f"SQL курс: http://{host}:{port}")
    ThreadingHTTPServer((host, port), Handler).serve_forever()
