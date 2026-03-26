from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

import pandas as pd

from app.actions import apply_actions_to_results
from app.config import AppConfig, get_config
from app.gmail_reader import fetch_messages_by_ids, fetch_recent_emails
from app.gmail_watch import GmailHistoryExpiredError, get_latest_history_id, list_history_message_ids, start_gmail_watch
from app.predictor import predict_emails
from app.storage import initialize_storage, load_app_state, merge_seen_message_ids, save_app_state, upsert_scan_history
from app.utils import timestamp_now


@dataclass(slots=True)
class MonitorSettings:
    """User-selected monitoring settings."""

    gmail_query: str
    max_emails: int
    confidence_threshold: float
    apply_gmail_label: bool
    monitor_mode: str


@dataclass(slots=True)
class MonitorCycleResult:
    """Structured output of a monitoring cycle."""

    results_df: pd.DataFrame
    new_email_count: int
    latest_history_id: str
    status_message: str
    monitor_mode: str
    used_fallback: bool = False


def _predict_and_store(
    email_records: List[Dict[str, Any]],
    service,
    settings: MonitorSettings,
    config: AppConfig,
) -> pd.DataFrame:
    if not email_records:
        return pd.DataFrame()

    results_df = predict_emails(email_records, confidence_threshold=settings.confidence_threshold, config=config)
    results_df["monitor_mode"] = settings.monitor_mode
    results_df = apply_actions_to_results(results_df, service, settings.apply_gmail_label, config)
    upsert_scan_history(results_df.to_dict(orient="records"), config=config)
    return results_df


def _filter_inbox_records(email_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Keep only inbox-style messages for monitoring flows."""
    return [record for record in email_records if "INBOX" in record.get("label_ids", [])]


def _update_state_after_cycle(
    state: Dict[str, Any],
    message_ids: List[str],
    latest_history_id: str,
    settings: MonitorSettings,
    config: AppConfig,
    error_message: str = "",
) -> None:
    state["seen_message_ids"] = merge_seen_message_ids(state.get("seen_message_ids", []), message_ids)
    state["last_history_id"] = latest_history_id or state.get("last_history_id", "")
    state["monitor_mode"] = settings.monitor_mode
    state["monitor_running"] = True
    state["last_scan_time"] = timestamp_now()
    state["last_error"] = error_message
    save_app_state(state, config)


def start_monitoring(service, settings: MonitorSettings, config: AppConfig | None = None) -> Dict[str, Any]:
    """Initialize monitoring state and optionally register Gmail watch mode."""
    active_config = config or get_config()
    initialize_storage(active_config)
    state = load_app_state(active_config)
    state["monitor_mode"] = settings.monitor_mode
    state["monitor_running"] = True
    state["last_scan_time"] = timestamp_now()
    state["last_error"] = ""
    state["last_history_id"] = get_latest_history_id(service)

    if settings.monitor_mode == "watch":
        watch_response = start_gmail_watch(
            service=service,
            topic_name=active_config.watch_topic_name,
            label_ids=["INBOX"],
            label_filter_action=active_config.watch_label_filter_behavior,
        )
        state["watch_expiration"] = str(watch_response.get("expiration", ""))

    save_app_state(state, active_config)
    return state


def stop_monitoring(config: AppConfig | None = None) -> Dict[str, Any]:
    """Persist a stopped monitor state."""
    active_config = config or get_config()
    state = load_app_state(active_config)
    state["monitor_running"] = False
    save_app_state(state, active_config)
    return state


def run_manual_scan(service, settings: MonitorSettings, config: AppConfig | None = None) -> MonitorCycleResult:
    """Scan the latest Gmail messages using the current query."""
    active_config = config or get_config()
    initialize_storage(active_config)
    state = load_app_state(active_config)
    email_records = fetch_recent_emails(service=service, max_results=settings.max_emails, query=settings.gmail_query)
    results_df = _predict_and_store(email_records, service, settings, active_config)
    latest_history_id = get_latest_history_id(service)
    _update_state_after_cycle(
        state=state,
        message_ids=[record.get("message_id", "") for record in email_records],
        latest_history_id=latest_history_id,
        settings=settings,
        config=active_config,
    )
    return MonitorCycleResult(
        results_df=results_df,
        new_email_count=len(email_records),
        latest_history_id=latest_history_id,
        status_message=f"Manual scan completed. Processed {len(email_records)} email(s).",
        monitor_mode=settings.monitor_mode,
    )


def _run_history_cycle(service, settings: MonitorSettings, config: AppConfig, state: Dict[str, Any]) -> MonitorCycleResult:
    history_response = list_history_message_ids(
        service=service,
        start_history_id=state.get("last_history_id", ""),
        max_results=config.history_fetch_limit,
    )
    latest_history_id = str(history_response.get("latest_history_id", state.get("last_history_id", "")))
    seen_ids = set(state.get("seen_message_ids", []))
    new_message_ids = [message_id for message_id in history_response.get("message_ids", []) if message_id not in seen_ids]
    email_records = _filter_inbox_records(fetch_messages_by_ids(service, new_message_ids))
    results_df = _predict_and_store(email_records, service, settings, config)
    _update_state_after_cycle(
        state=state,
        message_ids=[record.get("message_id", "") for record in email_records],
        latest_history_id=latest_history_id,
        settings=settings,
        config=config,
    )
    return MonitorCycleResult(
        results_df=results_df,
        new_email_count=len(email_records),
        latest_history_id=latest_history_id,
        status_message=(
            "History check completed. No new inbox messages were found."
            if not email_records
            else f"History check completed. Processed {len(email_records)} new email(s)."
        ),
        monitor_mode=settings.monitor_mode,
    )


def _run_polling_cycle(service, settings: MonitorSettings, config: AppConfig, state: Dict[str, Any]) -> MonitorCycleResult:
    email_records = fetch_recent_emails(
        service=service,
        max_results=settings.max_emails,
        query=settings.gmail_query,
        exclude_message_ids=state.get("seen_message_ids", []),
        candidate_limit=settings.max_emails * 5,
    )
    latest_history_id = get_latest_history_id(service)
    results_df = _predict_and_store(email_records, service, settings, config)
    _update_state_after_cycle(
        state=state,
        message_ids=[record.get("message_id", "") for record in email_records],
        latest_history_id=latest_history_id,
        settings=settings,
        config=config,
    )
    return MonitorCycleResult(
        results_df=results_df,
        new_email_count=len(email_records),
        latest_history_id=latest_history_id,
        status_message=(
            "Polling cycle completed. No new inbox messages were found."
            if not email_records
            else f"Polling cycle completed. Processed {len(email_records)} new email(s)."
        ),
        monitor_mode=settings.monitor_mode,
    )


def run_monitor_cycle(service, settings: MonitorSettings, config: AppConfig | None = None) -> MonitorCycleResult:
    """Run one monitoring cycle using watch/history or polling fallback."""
    active_config = config or get_config()
    initialize_storage(active_config)
    state = load_app_state(active_config)
    selected_mode = settings.monitor_mode.lower()

    if selected_mode in {"watch", "history"} and state.get("last_history_id"):
        try:
            return _run_history_cycle(service, settings, active_config, state)
        except GmailHistoryExpiredError as error:
            polling_result = _run_polling_cycle(service, settings, active_config, state)
            polling_result.used_fallback = True
            polling_result.status_message = (
                f"History checkpoint expired, so polling fallback was used. {polling_result.status_message}"
            )
            state = load_app_state(active_config)
            state["last_error"] = str(error)
            save_app_state(state, active_config)
            return polling_result

    return _run_polling_cycle(service, settings, active_config, state)
