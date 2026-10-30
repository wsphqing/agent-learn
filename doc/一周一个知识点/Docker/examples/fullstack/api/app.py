"""Docker learning lab: deliberately small synchronous HTTP + PostgreSQL API."""
import json
import os
import signal
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import psycopg


def connect():
    return psycopg.connect(
        host=os.environ.get("DB_HOST", "db"),
        dbname=os.environ.get("DB_NAME", "lab"),
        user=os.environ.get("DB_USER", "lab"),
        password=Path(os.environ["DB_PASSWORD_FILE"]).read_text().strip(),
        connect_timeout=3,
        options="-c statement_timeout=3000",
    )


def initialize():
    for attempt in range(30):
        try:
            with connect() as db:
                db.execute("CREATE TABLE IF NOT EXISTS counter (id integer PRIMARY KEY, value integer NOT NULL)")
                db.execute("INSERT INTO counter VALUES (1, 0) ON CONFLICT (id) DO NOTHING")
            return
        except psycopg.OperationalError:
            if attempt == 29:
                raise
            time.sleep(2)


class Handler(BaseHTTPRequestHandler):
    def respond(self, code, data):
        payload = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def dispatch(self, increment=False):
        path = self.path.split("?", 1)[0]
        if (increment and path != "/api/visits") or path not in ("/api/health", "/api/visits"):
            self.respond(404, {"error": "not found"})
            return
        try:
            with connect() as db:
                if path == "/api/health":
                    db.execute("SELECT 1")
                    result = {"status": "ok"}
                elif increment:
                    value = db.execute("UPDATE counter SET value = value + 1 WHERE id = 1 RETURNING value").fetchone()[0]
                    result = {"visits": value}
                else:
                    value = db.execute("SELECT value FROM counter WHERE id = 1").fetchone()[0]
                    result = {"visits": value}
            self.respond(200, result)
        except psycopg.Error:
            self.log_error("database operation failed")
            self.respond(503, {"error": "database temporarily unavailable"})

    def do_GET(self):
        self.dispatch()

    def do_POST(self):
        self.dispatch(increment=True)


if __name__ == "__main__":
    initialize()
    server = ThreadingHTTPServer(("0.0.0.0", 8000), Handler)
    # shutdown() must run in a different thread from serve_forever().
    signal.signal(signal.SIGTERM, lambda *_: threading.Thread(target=server.shutdown, daemon=True).start())
    print("API listening on 0.0.0.0:8000", flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()
