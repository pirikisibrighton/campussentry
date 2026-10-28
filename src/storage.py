import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "campussentry.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                report_text TEXT NOT NULL,
                category TEXT NOT NULL,
                severity TEXT NOT NULL,
                language TEXT NOT NULL,
                location TEXT NOT NULL DEFAULT '[]',
                entities TEXT NOT NULL DEFAULT '[]',
                status TEXT NOT NULL DEFAULT 'New'
            )
        """)
        connection.commit()


def save_incident(report_text, analysis):
    with get_connection() as connection:
        cursor = connection.execute("""
            INSERT INTO incidents (
                created_at, report_text, category, severity,
                language, location, entities, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'New')
        """, (
            datetime.now(timezone.utc).isoformat(timespec="seconds"),
            report_text,
            analysis["category"],
            analysis["severity"],
            analysis["language"],
            json.dumps(analysis.get("location", [])),
            json.dumps(analysis.get("entities", [])),
        ))
        connection.commit()
        return cursor.lastrowid


def get_incidents():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM incidents ORDER BY id DESC"
        ).fetchall()

    incidents = []
    for row in rows:
        item = dict(row)
        item["location"] = json.loads(item["location"])
        item["entities"] = json.loads(item["entities"])
        incidents.append(item)

    return incidents


def update_status(incident_id, status):
    allowed = {"New", "Under Review", "Resolved"}
    if status not in allowed:
        raise ValueError("Invalid incident status.")

    with get_connection() as connection:
        connection.execute(
            "UPDATE incidents SET status = ? WHERE id = ?",
            (status, incident_id),
        )
        connection.commit()
