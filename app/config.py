from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODEL_DIR = PROJECT_ROOT / "model"


@dataclass(slots=True)
class AppConfig:
    """Central application configuration loaded from the environment."""

    project_root: Path = PROJECT_ROOT
    data_dir: Path = DATA_DIR
    model_dir: Path = MODEL_DIR
    dataset_path: Path = PROJECT_ROOT / os.getenv("DATASET_PATH", "data/phishing_dataset.csv")
    processed_dataset_path: Path = PROJECT_ROOT / os.getenv("PROCESSED_DATASET_PATH", "data/processed_dataset.csv")
    scan_history_csv_path: Path = PROJECT_ROOT / os.getenv("SCAN_HISTORY_PATH", "data/scan_history.csv")
    scan_history_db_path: Path = PROJECT_ROOT / os.getenv("SCAN_HISTORY_DB_PATH", "data/scan_history.db")
    app_state_path: Path = PROJECT_ROOT / os.getenv("APP_STATE_PATH", "data/app_state.json")
    model_path: Path = PROJECT_ROOT / os.getenv("MODEL_PATH", "model/phishing_model.pkl")
    vectorizer_path: Path = PROJECT_ROOT / os.getenv("VECTORIZER_PATH", "model/vectorizer.pkl")
    metadata_path: Path = PROJECT_ROOT / os.getenv("METADATA_PATH", "model/model_metadata.json")
    credentials_path: Path = PROJECT_ROOT / os.getenv("GMAIL_CREDENTIALS_PATH", "credentials.json")
    token_path: Path = PROJECT_ROOT / os.getenv("GMAIL_TOKEN_PATH", "token.json")
    default_gmail_query: str = os.getenv("DEFAULT_GMAIL_QUERY", "category:primary OR category:updates OR in:inbox")
    max_email_fetch: int = int(os.getenv("MAX_EMAIL_FETCH", "20"))
    polling_interval_seconds: int = int(os.getenv("LIVE_SCAN_INTERVAL_SECONDS", "30"))
    confidence_threshold: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.55"))
    history_fetch_limit: int = int(os.getenv("HISTORY_FETCH_LIMIT", "100"))
    watch_topic_name: str = os.getenv("GMAIL_WATCH_TOPIC_NAME", "")
    watch_label_filter_behavior: str = os.getenv("GMAIL_WATCH_LABEL_FILTER_ACTION", "include")
    apply_gmail_label_by_default: bool = os.getenv("APPLY_GMAIL_LABEL_DEFAULT", "false").lower() == "true"
    phishing_label_name: str = os.getenv("PHISHING_LABEL_NAME", "Suspected Phishing")

    def ensure_directories(self) -> None:
        """Create local data directories if they do not exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.scan_history_csv_path.parent.mkdir(parents=True, exist_ok=True)
        self.scan_history_db_path.parent.mkdir(parents=True, exist_ok=True)
        self.app_state_path.parent.mkdir(parents=True, exist_ok=True)


def get_config() -> AppConfig:
    """Return the current application configuration."""
    config = AppConfig()
    config.ensure_directories()
    return config


def get_setup_status(config: AppConfig | None = None) -> dict[str, bool]:
    """Return a simple readiness snapshot for local project requirements."""
    active_config = config or get_config()
    return {
        "dataset_exists": active_config.dataset_path.exists(),
        "model_exists": active_config.model_path.exists(),
        "vectorizer_exists": active_config.vectorizer_path.exists(),
        "metadata_exists": active_config.metadata_path.exists(),
        "credentials_exists": active_config.credentials_path.exists(),
        "token_exists": active_config.token_path.exists(),
        "watch_configured": bool(active_config.watch_topic_name.strip()),
    }
