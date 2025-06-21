import sqlite3
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "friday_memory.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "friday_memory_schema.sql")

class FridayMemoryManager:
    def __init__(self, db_path: str = DB_PATH, schema_path: str = SCHEMA_PATH):
        self.db_path = db_path
        self.schema_path = schema_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        with open(self.schema_path, "r") as f:
            self.conn.executescript(f.read())
        self.conn.commit()

    def get_active_session(self) -> Dict[str, Any]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM session WHERE active=1 LIMIT 1;")
        row = cur.fetchone()
        if row:
            return dict(row)
        now = datetime.utcnow().isoformat()
        cur.execute("INSERT INTO session (started_at, tags) VALUES (?, ?)", (now, json.dumps([])))
        self.conn.commit()
        return self.get_active_session()

    def end_active_session(self, tags: Optional[List[str]] = None) -> None:
        cur = self.conn.cursor()
        now = datetime.utcnow().isoformat()
        active = self.get_active_session()
        t = json.dumps(tags or [])
        cur.execute(
            "UPDATE session SET ended_at=?, active=0, tags=? WHERE id=?",
            (now, t, active['id'])
        )
        self.conn.commit()

    def add_message(self, role: str, content: str, tags: Optional[List[str]] = None) -> None:
        session = self.get_active_session()
        cur = self.conn.cursor()
        now = datetime.utcnow().isoformat()
        t = json.dumps(tags or [])
        cur.execute(
            "INSERT INTO message (session_id, role, content, tags, timestamp) VALUES (?, ?, ?, ?, ?)",
            (session['id'], role, content, t, now)
        )
        self.conn.commit()

    def get_session_messages(self, session_id: Optional[int] = None) -> List[Dict[str, Any]]:
        session = self.get_active_session() if session_id is None else {'id': session_id}
        cur = self.conn.cursor()
        cur.execute(
            "SELECT role, content, tags, timestamp FROM message WHERE session_id=? ORDER BY id ASC",
            (session['id'],)
        )
        return [dict(row) for row in cur.fetchall()]

    def get_active_session_messages(self) -> List[Dict[str, Any]]:
        session = self.get_active_session()
        return self.get_session_messages(session_id=session["id"])

    def get_recent_messages(self, n: int = 10) -> List[Dict[str, Any]]:
        session = self.get_active_session()
        cur = self.conn.cursor()
        cur.execute(
            "SELECT role, content, tags, timestamp FROM message WHERE session_id=? ORDER BY id DESC LIMIT ?",
            (session['id'], n)
        )
        rows = cur.fetchall()
        return [dict(row) for row in reversed(rows)]

    def get_messages_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        session = self.get_active_session()
        cur = self.conn.cursor()
        cur.execute(
            "SELECT role, content, tags, timestamp FROM message WHERE session_id=? ORDER BY id ASC",
            (session['id'],)
        )
        rows = []
        for row in cur.fetchall():
            tags = json.loads(row["tags"])
            if tag in tags:
                rows.append(dict(row))
        return rows

    def get_all_sessions(self) -> List[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM session ORDER BY started_at DESC")
        return [dict(row) for row in cur.fetchall()]

    def get_session_by_id(self, session_id: int) -> Optional[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM session WHERE id=?", (session_id,))
        row = cur.fetchone()
        return dict(row) if row else None

# Usage Example
if __name__ == "__main__":
    mm = FridayMemoryManager()
    mm.add_message("user", "Foundation memory test!", tags=["test", "foundation"])
    mm.add_message("friday", "Memory system is green. 🧼", tags=["system", "confirmation"])
    print(mm.get_active_session_messages())
