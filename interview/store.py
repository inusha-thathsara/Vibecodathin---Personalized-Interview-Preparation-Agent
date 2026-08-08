import sqlite3
import json
import logging
import time
from typing import Dict, Any, Optional, List
import config

logger = logging.getLogger(__name__)

class SessionStore:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = str(db_path or config.SESSIONS_DB_FILE)
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        try:
            config.DATA_DIR.mkdir(parents=True, exist_ok=True)
            with self._get_connection() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        session_id TEXT PRIMARY KEY,
                        data TEXT NOT NULL,
                        created_at REAL NOT NULL,
                        last_active_at REAL NOT NULL
                    )
                """)
                conn.commit()
            logger.info(f"SQLite SessionStore initialized at {self.db_path}")
        except Exception as e:
            logger.warning(f"Could not initialize SQLite SessionStore ({e}). Fallback to in-memory.")

    def save_session(self, session_dict: Dict[str, Any]):
        session_id = session_dict.get("session_id")
        if not session_id:
            return
        
        try:
            data_json = json.dumps(session_dict)
            now = time.time()
            created = session_dict.get("created_at", now)
            last_active = session_dict.get("last_active_at", now)

            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO sessions (session_id, data, created_at, last_active_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(session_id) DO UPDATE SET
                        data = excluded.data,
                        last_active_at = excluded.last_active_at
                """, (session_id, data_json, created, last_active))
                conn.commit()
        except Exception as e:
            logger.warning(f"Error saving session '{session_id}' to SQLite: {e}")

    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        try:
            with self._get_connection() as conn:
                row = conn.execute("SELECT data FROM sessions WHERE session_id = ?", (session_id,)).fetchone()
                if row:
                    return json.loads(row["data"])
        except Exception as e:
            logger.warning(f"Error loading session '{session_id}' from SQLite: {e}")
        return None

    def delete_session(self, session_id: str):
        try:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
                conn.commit()
        except Exception as e:
            logger.warning(f"Error deleting session '{session_id}' from SQLite: {e}")

    def cleanup_expired_sessions(self, ttl_seconds: float = 7200) -> int:
        """Purges sessions inactive for longer than ttl_seconds (default 2 hours)."""
        cutoff = time.time() - ttl_seconds
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("DELETE FROM sessions WHERE last_active_at < ?", (cutoff,))
                deleted = cursor.rowcount
                conn.commit()
                if deleted > 0:
                    logger.info(f"Cleaned up {deleted} expired idle sessions.")
                return deleted
        except Exception as e:
            logger.warning(f"Error cleaning up expired sessions: {e}")
            return 0

session_store = SessionStore()
