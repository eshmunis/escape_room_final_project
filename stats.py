"""
Minimal SQLite logger for game runs.

Creates data/runs.sqlite (if missing) and stores each run with:
- ts (ISO timestamp)
- escaped (0/1)
- duration_sec (int)

Also exposes best_time() so the game can show a “fastest escape” banner.
"""

import os
import sqlite3
from datetime import datetime

DB_PATH_DEFAULT = os.path.join("data", "runs.sqlite")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    escaped INTEGER NOT NULL,
    duration_sec INTEGER NOT NULL
);
"""

def ensure_data_dir():
    """
    Make sure the data directory exists.

    Returns:
        None

    Side Effects:
        Creates the "data/" folder if it doesn't exist.
    """
    os.makedirs("data", exist_ok=True)

def init_db(db_path: str = DB_PATH_DEFAULT) -> None:
    """
    Create the database file/tables if they don’t exist yet.

    Parameters:
        db_path (str): Filesystem path to the SQLite file.

    Returns:
        None

    Side Effects:
        Opens/creates the SQLite file and ensures the schema exists.
    """
    ensure_data_dir()
    with sqlite3.connect(db_path) as conn:
        conn.execute(_SCHEMA)
        conn.commit()

def record_run(escaped: bool, duration_sec: int, db_path: str = DB_PATH_DEFAULT) -> None:
    """
    Insert a completed run (escape, timeout, or manual quit if you choose).

    Parameters:
        escaped (bool): True if the player escaped, False otherwise.
        duration_sec (int): How long the run lasted, in whole seconds.
        db_path (str): Path to the SQLite file.

    Returns:
        None

    Side Effects:
        Writes a row into the "runs" table.
    """
    ensure_data_dir()
    ts = datetime.now().isoformat(timespec="seconds")
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO runs (ts, escaped, duration_sec) VALUES (?, ?, ?)",
            (ts, 1 if escaped else 0, int(duration_sec)),
        )
        conn.commit()

def best_time(db_path: str = DB_PATH_DEFAULT) -> int | None:
    """
    Get the fastest (minimum) escape time.

    Parameters:
        db_path (str): Path to the SQLite file.

    Returns:
        int | None: Best duration in seconds, or None if there are no wins.

    Side Effects:
        Opens the database to read results.
    """
    ensure_data_dir()
    with sqlite3.connect(db_path) as conn:
        cur = conn.execute("SELECT MIN(duration_sec) FROM runs WHERE escaped=1")
        row = cur.fetchone()
        if not row:
            return None
        best = row[0]
        return int(best) if best is not None else None