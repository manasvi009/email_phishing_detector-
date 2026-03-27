from __future__ import annotations

import json
import sqlite3
from typing import Any, Dict, Iterable, List

import pandas as pd

from app.config import AppConfig, get_config


DEFAULT_APP_STATE = {
    "last_history_id": "",
    "watch_expiration": "",
    "seen_message_ids": [],
    "monitor_mode": "polling",
    "monitor_running": False,
    "last_scan_time": "",
    "last_error": "",
}


def get_db_connection(config: AppConfig | None = None) -> sqlite3.Connection:
    """Open the local SQLite database used for scan history."""
    active_config = config or get_config()
    return sqlite3.connect(active_config.scan_history_db_path)


def initialize_storage(config: AppConfig | None = None) -> None:
    """Create storage artifacts required by the application."""
    active_config = config or get_config()
    active_config.ensure_directories()

    connection = get_db_connection(active_config)
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_time TEXT NOT NULL,
                message_id TEXT NOT NULL UNIQUE,
                thread_id TEXT,
                sender_name TEXT,
                sender_email TEXT,
                subject TEXT,
                date TEXT,
                snippet TEXT,
                label TEXT,
                risk_score REAL,
                confidence REAL,
                risk_badge TEXT,
                reasons TEXT,
                headers_json TEXT,
                body_text TEXT,
                model_name TEXT,
                monitor_mode TEXT,
                gmail_label_applied INTEGER DEFAULT 0
            )
            """
        )
        connection.commit()
    finally:
        connection.close()

    if not active_config.app_state_path.exists():
        save_app_state(DEFAULT_APP_STATE, active_config)


def load_app_state(config: AppConfig | None = None) -> Dict[str, Any]:
    """Load persisted application state from disk."""
    active_config = config or get_config()
    if not active_config.app_state_path.exists():
        return DEFAULT_APP_STATE.copy()

    try:
        with active_config.app_state_path.open("r", encoding="utf-8") as file:
            raw_content = file.read().strip()
            if not raw_content:
                save_app_state(DEFAULT_APP_STATE, active_config)
                return DEFAULT_APP_STATE.copy()
            persisted = json.loads(raw_content)
    except (json.JSONDecodeError, OSError):
        save_app_state(DEFAULT_APP_STATE, active_config)
        return DEFAULT_APP_STATE.copy()

    state = DEFAULT_APP_STATE.copy()
    state.update(persisted)
    return state


def save_app_state(state: Dict[str, Any], config: AppConfig | None = None) -> None:
    """Persist application state to disk."""
    active_config = config or get_config()
    payload = DEFAULT_APP_STATE.copy()
    payload.update(state)
    with active_config.app_state_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)


def upsert_scan_history(rows: List[Dict[str, Any]], config: AppConfig | None = None) -> None:
    """Store scan results in SQLite and refresh the CSV export."""
    if not rows:
        return

    active_config = config or get_config()
    initialize_storage(active_config)

    prepared_rows: List[Dict[str, Any]] = []
    for row in rows:
        prepared_rows.append(
            {
                "scan_time": row.get("scan_time", ""),
                "message_id": row.get("message_id", ""),
                "thread_id": row.get("thread_id", ""),
                "sender_name": row.get("sender_name", ""),
                "sender_email": row.get("sender_email", ""),
                "subject": row.get("subject", ""),
                "date": row.get("date", ""),
                "snippet": row.get("preview", row.get("snippet", "")),
                "label": row.get("label", ""),
                "risk_score": row.get("risk_score", 0.0),
                "confidence": row.get("confidence", 0.0),
                "risk_badge": row.get("risk_badge", ""),
                "reasons": " | ".join(row.get("reasons", [])) if isinstance(row.get("reasons"), list) else str(row.get("reasons", "")),
                "headers_json": json.dumps(row.get("headers", {})),
                "body_text": row.get("body_text", ""),
                "model_name": row.get("model_name", ""),
                "monitor_mode": row.get("monitor_mode", "polling"),
                "gmail_label_applied": int(bool(row.get("label_applied", False))),
            }
        )

    connection = get_db_connection(active_config)
    try:
        for row in prepared_rows:
            connection.execute(
                """
                INSERT OR REPLACE INTO scan_history (
                    scan_time, message_id, thread_id, sender_name, sender_email,
                    subject, date, snippet, label, risk_score, confidence,
                    risk_badge, reasons, headers_json, body_text, model_name,
                    monitor_mode, gmail_label_applied
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["scan_time"],
                    row["message_id"],
                    row["thread_id"],
                    row["sender_name"],
                    row["sender_email"],
                    row["subject"],
                    row["date"],
                    row["snippet"],
                    row["label"],
                    row["risk_score"],
                    row["confidence"],
                    row["risk_badge"],
                    row["reasons"],
                    row["headers_json"],
                    row["body_text"],
                    row["model_name"],
                    row["monitor_mode"],
                    row["gmail_label_applied"],
                ),
            )
        connection.commit()
    finally:
        connection.close()

    export_scan_history_to_csv(active_config)


def export_scan_history_to_csv(config: AppConfig | None = None) -> None:
    """Refresh the CSV history export from SQLite."""
    active_config = config or get_config()
    connection = get_db_connection(active_config)
    try:
        df = pd.read_sql_query(
            "SELECT * FROM scan_history ORDER BY scan_time DESC, risk_score DESC",
            connection,
        )
    finally:
        connection.close()
    df.to_csv(active_config.scan_history_csv_path, index=False)


def load_scan_history(config: AppConfig | None = None, limit: int | None = None) -> pd.DataFrame:
    """Read scan history from SQLite."""
    active_config = config or get_config()
    initialize_storage(active_config)
    query = "SELECT * FROM scan_history ORDER BY scan_time DESC, risk_score DESC"
    if limit:
        query += f" LIMIT {int(limit)}"

    connection = get_db_connection(active_config)
    try:
        df = pd.read_sql_query(query, connection)
    finally:
        connection.close()

    if df.empty:
        return pd.DataFrame()

    df["headers"] = df["headers_json"].apply(lambda value: json.loads(value) if value else {})
    df["reasons"] = df["reasons"].apply(lambda value: value.split(" | ") if value else [])
    df["label_applied"] = df["gmail_label_applied"].astype(bool)
    df["preview"] = df["snippet"]
    return df.drop(columns=["headers_json", "gmail_label_applied"], errors="ignore")


def merge_seen_message_ids(
    existing_ids: Iterable[str],
    new_ids: Iterable[str],
    max_items: int = 5000,
) -> List[str]:
    """Combine known message ids while keeping the list bounded."""
    merged = [message_id for message_id in existing_ids if message_id]
    existing_lookup = set(merged)
    for message_id in new_ids:
        if message_id and message_id not in existing_lookup:
            merged.append(message_id)
            existing_lookup.add(message_id)
    return merged[-max_items:]
