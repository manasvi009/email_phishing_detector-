from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List

import pandas as pd

from app.config import get_config


def ensure_directories() -> None:
    """Create required directories if they are missing."""
    get_config().ensure_directories()


def get_env_path(key: str, default: str) -> Path:
    """Read a relative path from .env and convert it into an absolute path."""
    return get_config().project_root / os.getenv(key, default)


def timestamp_now() -> str:
    """Return a local timestamp string used in reports and history."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def timestamp_now_utc() -> str:
    """Return a UTC timestamp string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def load_json(path: Path, default: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Load JSON data, returning a default dict if the file is missing."""
    if not path.exists():
        return default or {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def append_scan_history(rows: List[Dict[str, Any]], history_path: Path | None = None) -> None:
    """Append scan rows to a CSV file."""
    path = history_path or get_env_path("SCAN_HISTORY_PATH", "data/scan_history.csv")
    path.parent.mkdir(parents=True, exist_ok=True)
    history_df = pd.DataFrame(rows)
    if path.exists():
        existing = pd.read_csv(path)
        history_df = pd.concat([existing, history_df], ignore_index=True)
    history_df.to_csv(path, index=False)


def export_dataframe(df: pd.DataFrame) -> bytes:
    """Convert a DataFrame to downloadable CSV bytes."""
    return df.to_csv(index=False).encode("utf-8")


def records_to_dataframe(records: Iterable[Dict[str, Any]]) -> pd.DataFrame:
    """Convert a list of dict records into a DataFrame."""
    return pd.DataFrame(list(records))
