from __future__ import annotations

import re


STOP_PHRASES = ["fw:", "fwd:", "re:"]
WHITESPACE_PATTERN = re.compile(r"\s+")
URL_PATTERN = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
EMAIL_PATTERN = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b", re.IGNORECASE)


def normalize_text(text: str) -> str:
    """Normalize email text while preserving phishing-relevant patterns."""
    if not text:
        return ""
    cleaned = text.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    cleaned = URL_PATTERN.sub(" URLTOKEN ", cleaned)
    cleaned = EMAIL_PATTERN.sub(" EMAILTOKEN ", cleaned)
    cleaned = re.sub(r"\d+", " NUMTOKEN ", cleaned)
    cleaned = re.sub(r"[^a-zA-Z0-9!?.:\-_/@ ]", " ", cleaned)
    cleaned = WHITESPACE_PATTERN.sub(" ", cleaned).strip().lower()
    return cleaned


def clean_subject(subject: str) -> str:
    """Remove repetitive prefixes such as RE and FWD from a subject line."""
    value = subject.strip()
    for prefix in STOP_PHRASES:
        if value.lower().startswith(prefix):
            value = value[len(prefix):].strip()
    return value


def normalize_sender(sender_name: str, sender_email: str) -> str:
    """Normalize sender display name and email into one analysis string."""
    return normalize_text(" ".join(part for part in [sender_name, sender_email] if part))


def preprocess_email_fields(
    subject: str,
    sender_email: str,
    body_text: str,
    snippet: str,
    sender_name: str = "",
) -> dict:
    """Apply consistent preprocessing across key email fields."""
    return {
        "clean_subject": normalize_text(clean_subject(subject)),
        "clean_sender_email": normalize_text(sender_email),
        "clean_sender": normalize_sender(sender_name, sender_email),
        "clean_body_text": normalize_text(body_text),
        "clean_snippet": normalize_text(snippet),
    }
