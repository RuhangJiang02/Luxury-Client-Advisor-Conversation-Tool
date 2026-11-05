"""SQLite evidence and request reservation for the local app and CLI."""

import json
import sqlite3
from pathlib import Path

from .config import ROOT


class RunStore:
    def __init__(self, path=None):
        self.path = Path(path) if path else ROOT / "runs/runs.sqlite3"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS runs (request_id TEXT PRIMARY KEY, identity TEXT NOT NULL, run_id TEXT NOT NULL UNIQUE, state TEXT NOT NULL, artifact TEXT)")
            db.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, request_id TEXT, artifact TEXT NOT NULL)")

    def connect(self):
        return sqlite3.connect(self.path, timeout=5)

    def reserve(self, request_id, identity, run_id):
        with self.connect() as db:
            inserted = db.execute("INSERT OR IGNORE INTO runs (request_id, identity, run_id, state) VALUES (?, ?, ?, 'pending')", (request_id, identity, run_id)).rowcount
            if inserted:
                return "new", None
            row = db.execute("SELECT identity, state, artifact FROM runs WHERE request_id=?", (request_id,)).fetchone()
            if row[0] != identity:
                return "conflict", None
            if row[1] == "pending":
                return "pending", None
            return "cached", json.loads(row[2])

    def finish(self, request_id, artifact):
        with self.connect() as db:
            db.execute("UPDATE runs SET state='complete', artifact=? WHERE request_id=? AND state='pending'", (json.dumps(artifact, ensure_ascii=False), request_id))

    def event(self, request_id, artifact):
        with self.connect() as db:
            db.execute("INSERT INTO events (request_id, artifact) VALUES (?, ?)", (request_id, json.dumps(artifact, ensure_ascii=False)))

    def artifacts(self):
        with self.connect() as db:
            rows = db.execute("SELECT artifact FROM runs WHERE state='complete' ORDER BY rowid").fetchall()
        return [json.loads(row[0]) for row in rows]
