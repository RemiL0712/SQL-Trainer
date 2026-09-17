import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

import server
from content import LEVELS


class AppTests(unittest.TestCase):
    def test_course_queries_and_sandbox(self):
        self.assertEqual(len(LEVELS), 15)
        self.assertEqual(sum(len(level["tasks"]) for level in LEVELS), 100)
        for li, level in enumerate(LEVELS):
            for ti, task in enumerate(level["tasks"]):
                meta = task[7] if len(task) > 7 else {}
                with self.subTest(level=li, task=ti):
                    server.sandbox(task[2], meta.get("mode", "read"), meta.get("target"))
        for query in ("DROP TABLE users", "SELECT * FROM users; DELETE FROM users", "WITH x AS (DELETE FROM users) SELECT * FROM x"):
            with self.assertRaises(ValueError, msg=query):
                server.sandbox(query)

    def test_signup_progress_and_lock(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(server, "DB", Path(folder) / "test.sqlite3"):
            server.init_db()
            http = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
            thread = threading.Thread(target=http.serve_forever, daemon=True)
            thread.start()
            base = f"http://127.0.0.1:{http.server_port}"
            cookie = ""

            def post(path, body):
                nonlocal cookie
                req = urllib.request.Request(base + path, json.dumps(body).encode(), {"Content-Type": "application/json", "Cookie": cookie})
                try:
                    with urllib.request.urlopen(req) as response:
                        if response.headers.get("Set-Cookie"):
                            cookie = response.headers["Set-Cookie"].split(";", 1)[0]
                        return response.status, json.load(response)
                except urllib.error.HTTPError as error:
                    return error.code, json.load(error)

            try:
                with urllib.request.urlopen(base + "/favicon.ico") as response:
                    self.assertEqual(response.status, 200)
                    self.assertEqual(response.headers.get_content_type(), "image/svg+xml")
                self.assertEqual(post("/api/register", {"name": "Тест", "email": "test@example.com", "password": "password123"})[0], 200)
                self.assertEqual(post("/api/check", {"level": 1, "task": 0, "query": LEVELS[1]["tasks"][0][2]})[0], 403)
                self.assertFalse(post("/api/check", {"level": 0, "task": 0, "query": "SELECT age FROM users"})[1]["correct"])
                self.assertTrue(post("/api/check", {"level": 0, "task": 0, "query": LEVELS[0]["tasks"][0][2]})[1]["correct"])
                for i in range(1, len(LEVELS[0]["tasks"])):
                    response = post("/api/check", {"level": 0, "task": i, "query": LEVELS[0]["tasks"][i][2]})[1]
                    self.assertTrue(response["correct"])
                self.assertEqual(response["progress"]["unlocked"], 1)
                with patch.object(server.Handler, "progress", return_value={"unlocked": 14, "solved": []}):
                    write = post("/api/check", {"level": 12, "task": 0, "query": LEVELS[12]["tasks"][0][2]})[1]
                    self.assertTrue(write["correct"])
                    schema = post("/api/check", {"level": 13, "task": 0, "query": LEVELS[13]["tasks"][0][2]})[1]
                    self.assertTrue(schema["correct"])
            finally:
                http.shutdown()
                http.server_close()


if __name__ == "__main__":
    unittest.main()
