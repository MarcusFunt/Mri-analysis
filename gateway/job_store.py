import sqlite3
import json
from pathlib import Path
from threading import Lock
from .settings import JOB_DB

class JobStore:
    def __init__(self, db_path: Path = JOB_DB):
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            state TEXT,
            paths TEXT,
            result TEXT
            )"""
        )
        self._lock = Lock()

    def create(self, job_id: str, paths: dict, state: str = "uploaded"):
        with self._lock:
            self._conn.execute(
                "INSERT INTO jobs (id, state, paths, result) VALUES (?, ?, ?, ?)",
                (job_id, state, json.dumps(paths), None),
            )
            self._conn.commit()

    def update_state(self, job_id: str, state: str):
        with self._lock:
            self._conn.execute(
                "UPDATE jobs SET state=? WHERE id=?",
                (state, job_id),
            )
            self._conn.commit()

    def set_result(self, job_id: str, result: dict, state: str = "done"):
        with self._lock:
            self._conn.execute(
                "UPDATE jobs SET state=?, result=? WHERE id=?",
                (state, json.dumps(result), job_id),
            )
            self._conn.commit()

    def get(self, job_id: str):
        cur = self._conn.execute(
            "SELECT state, paths, result FROM jobs WHERE id=?", (job_id,)
        )
        row = cur.fetchone()
        if not row:
            return None
        state, paths, result = row
        return {
            "state": state,
            "paths": json.loads(paths),
            "result": json.loads(result) if result else None,
        }
