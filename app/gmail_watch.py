from __future__ import annotations

from typing import Dict, List


class GmailHistoryExpiredError(RuntimeError):
    """Raised when Gmail history can no longer continue from a saved history id."""


def get_profile(service) -> Dict:
    """Fetch the Gmail profile for the authenticated account."""
    return service.users().getProfile(userId="me").execute()


def get_latest_history_id(service) -> str:
    """Return the latest Gmail history id for the account."""
    return str(get_profile(service).get("historyId", ""))


def start_gmail_watch(
    service,
    topic_name: str,
    label_ids: List[str] | None = None,
    label_filter_action: str = "include",
) -> Dict:
    """Register a Gmail watch request backed by Google Pub/Sub."""
    if not topic_name:
        raise ValueError("A Pub/Sub topic name is required for Gmail watch mode.")

    body = {
        "topicName": topic_name,
        "labelFilterBehavior": label_filter_action.lower(),
    }
    if label_ids:
        body["labelIds"] = label_ids

    return service.users().watch(userId="me", body=body).execute()


def stop_gmail_watch(service) -> Dict:
    """Stop the active Gmail watch configuration."""
    return service.users().stop(userId="me").execute()


def list_history_message_ids(
    service,
    start_history_id: str,
    history_types: List[str] | None = None,
    max_results: int = 100,
) -> Dict[str, object]:
    """Return changed message ids since the saved history id."""
    if not start_history_id:
        return {"message_ids": [], "latest_history_id": ""}

    history_types = history_types or ["messageAdded"]
    page_token = None
    message_ids: List[str] = []
    latest_history_id = start_history_id

    while True:
        try:
            response = (
                service.users()
                .history()
                .list(
                    userId="me",
                    startHistoryId=start_history_id,
                    historyTypes=history_types,
                    maxResults=max_results,
                    pageToken=page_token,
                )
                .execute()
            )
        except Exception as error:  # noqa: BLE001
            message = str(error).lower()
            if "starthistoryid" in message or "historyid" in message:
                raise GmailHistoryExpiredError(str(error)) from error
            raise

        latest_history_id = str(response.get("historyId", latest_history_id))
        for history_entry in response.get("history", []):
            latest_history_id = str(history_entry.get("id", latest_history_id))
            for added_message in history_entry.get("messagesAdded", []):
                message = added_message.get("message", {})
                message_id = message.get("id")
                if message_id and message_id not in message_ids:
                    message_ids.append(message_id)

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    return {"message_ids": message_ids, "latest_history_id": latest_history_id}
