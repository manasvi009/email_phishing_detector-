from __future__ import annotations

from typing import Dict, Iterable, List

from app.parser import parse_gmail_message


def fetch_message_by_id(service, message_id: str) -> Dict:
    """Fetch a single Gmail message in full format."""
    message = (
        service.users()
        .messages()
        .get(userId="me", id=message_id, format="full")
        .execute()
    )
    return parse_gmail_message(message)


def fetch_recent_emails(
    service,
    max_results: int = 20,
    query: str = "in:inbox",
    exclude_message_ids: Iterable[str] | None = None,
    candidate_limit: int | None = None,
) -> List[Dict]:
    """Fetch recent Gmail messages and parse them into structured records."""
    excluded_ids = {message_id for message_id in (exclude_message_ids or []) if message_id}
    requested_candidates = max(max_results, candidate_limit or max_results)
    response = (
        service.users()
        .messages()
        .list(userId="me", maxResults=min(requested_candidates, 100), q=query)
        .execute()
    )
    messages = response.get("messages", [])
    parsed_messages: List[Dict] = []

    for item in messages:
        if item.get("id") in excluded_ids:
            continue
        parsed_messages.append(fetch_message_by_id(service, item["id"]))
        if len(parsed_messages) >= max_results:
            break

    return parsed_messages


def fetch_messages_by_ids(service, message_ids: Iterable[str]) -> List[Dict]:
    """Fetch multiple Gmail messages by id."""
    return [fetch_message_by_id(service, message_id) for message_id in message_ids if message_id]
