from __future__ import annotations

import base64
import re
from email.utils import parsedate_to_datetime
from typing import Any, Dict, List

from bs4 import BeautifulSoup


def decode_base64url(data: str) -> str:
    """Decode Gmail API base64url content into text."""
    if not data:
        return ""
    decoded_bytes = base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))
    return decoded_bytes.decode("utf-8", errors="ignore")


def extract_headers(headers: List[Dict[str, str]]) -> Dict[str, str]:
    """Convert Gmail header list into a lowercase lookup dict."""
    return {header["name"].lower(): header["value"] for header in headers if "name" in header}


def html_to_text(html_content: str) -> str:
    """Convert HTML email content to readable text."""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    return re.sub(r"\s+", " ", text).strip()


def extract_text_from_parts(payload: Dict[str, Any]) -> str:
    """Recursively read plain text and HTML parts from a Gmail payload."""
    mime_type = payload.get("mimeType", "")
    body_data = payload.get("body", {}).get("data", "")
    parts = payload.get("parts", []) or []

    if mime_type == "text/plain" and body_data:
        return decode_base64url(body_data)
    if mime_type == "text/html" and body_data:
        return html_to_text(decode_base64url(body_data))

    collected_text = []
    for part in parts:
        text = extract_text_from_parts(part)
        if text:
            collected_text.append(text)

    if not collected_text and body_data:
        raw_text = decode_base64url(body_data)
        return html_to_text(raw_text) if "<html" in raw_text.lower() else raw_text

    return "\n".join(collected_text).strip()


def split_sender(sender_header: str) -> tuple[str, str]:
    """Split a From header into sender name and sender email."""
    if not sender_header:
        return "", ""
    match = re.search(r"(.*)<(.+@.+)>", sender_header)
    if match:
        sender_name = match.group(1).strip().strip('"')
        sender_email = match.group(2).strip()
        return sender_name, sender_email
    return "", sender_header.strip()


def extract_links_from_text(text: str) -> List[str]:
    """Collect URL-like strings from decoded content."""
    if not text:
        return []
    return re.findall(r"https?://\S+|www\.\S+", text, flags=re.IGNORECASE)


def parse_gmail_message(message: Dict[str, Any]) -> Dict[str, Any]:
    """Parse a Gmail API message response into a clean email record."""
    payload = message.get("payload", {})
    headers = extract_headers(payload.get("headers", []))
    sender_name, sender_email = split_sender(headers.get("from", ""))
    body_text = extract_text_from_parts(payload)
    snippet = message.get("snippet", "") or ""
    links = extract_links_from_text(f"{snippet} {body_text}")

    date_value = headers.get("date", "")
    parsed_date = ""
    if date_value:
        try:
            parsed_date = parsedate_to_datetime(date_value).strftime("%Y-%m-%d %H:%M:%S")
        except (TypeError, ValueError, OverflowError):
            parsed_date = date_value

    return {
        "message_id": message.get("id", ""),
        "thread_id": message.get("threadId", ""),
        "history_id": str(message.get("historyId", "")),
        "internal_date": message.get("internalDate", ""),
        "label_ids": message.get("labelIds", []),
        "sender_name": sender_name,
        "sender_email": sender_email,
        "subject": headers.get("subject", ""),
        "snippet": snippet,
        "body_text": body_text,
        "date": parsed_date,
        "link_count": len(links),
        "links": links,
        "headers": {
            "from": headers.get("from", ""),
            "to": headers.get("to", ""),
            "cc": headers.get("cc", ""),
            "bcc": headers.get("bcc", ""),
            "reply-to": headers.get("reply-to", ""),
            "return-path": headers.get("return-path", ""),
            "message-id": headers.get("message-id", ""),
            "received-spf": headers.get("received-spf", ""),
            "authentication-results": headers.get("authentication-results", ""),
            "dkim-signature": headers.get("dkim-signature", ""),
            "delivered-to": headers.get("delivered-to", ""),
        },
    }
