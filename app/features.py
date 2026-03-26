from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd

from app.preprocess import preprocess_email_fields


URGENT_WORDS = {
    "urgent", "immediately", "final warning", "act now", "verify now", "click immediately",
    "login now", "action required", "attention", "suspended", "disabled", "restricted",
}
ACCOUNT_SUSPENSION_WORDS = {
    "account suspended", "mailbox disabled", "security alert", "account locked",
    "verify your account", "confirm your account", "reactivate", "unusual sign in",
}
PASSWORD_RESET_WORDS = {
    "password reset", "reset password", "change password", "password expires", "update password",
}
PRIZE_WORDS = {"winner", "lottery", "prize", "gift card", "reward", "claim now"}
PAYMENT_WORDS = {
    "invoice", "payment", "wire transfer", "bank transfer", "crypto", "wallet",
    "outstanding balance", "refund", "settlement",
}
SENSITIVE_INFO_WORDS = {
    "password", "pin", "cvv", "otp", "ssn", "social security", "credentials",
    "recovery phrase", "seed phrase", "security code",
}
IMPERSONATION_NAMES = {
    "support team", "security team", "billing department", "admin", "helpdesk",
    "microsoft support", "google support", "paypal support", "bank security",
}
SHORT_CTA_PHRASES = {"verify now", "login now", "act now", "click now", "open immediately", "update now"}
TRUSTED_DOMAINS = {
    "google.com", "gmail.com", "outlook.com", "microsoft.com", "amazon.com",
    "paypal.com", "apple.com", "linkedin.com", "github.com",
}


def extract_domain(email_address: str) -> str:
    """Extract the sender domain from an email address."""
    if "@" not in email_address:
        return ""
    return email_address.split("@", 1)[1].strip().lower()


def count_matches(text: str, keywords: set[str]) -> int:
    """Count keyword matches inside text."""
    lowered = text.lower()
    return sum(1 for keyword in keywords if keyword in lowered)


def uppercase_ratio(text: str) -> float:
    """Compute uppercase density within text."""
    letters = [character for character in text if character.isalpha()]
    if not letters:
        return 0.0
    uppercase_letters = sum(1 for character in letters if character.isupper())
    return uppercase_letters / len(letters)


def number_ratio(text: str) -> float:
    """Compute numeric density within text."""
    if not text:
        return 0.0
    return sum(1 for character in text if character.isdigit()) / max(len(text), 1)


def special_character_ratio(text: str) -> float:
    """Compute symbol density within text."""
    if not text:
        return 0.0
    special_count = sum(1 for character in text if not character.isalnum() and not character.isspace())
    return special_count / max(len(text), 1)


def suspicious_sender_domain(sender_domain: str) -> bool:
    """Detect suspicious sender domain patterns."""
    if not sender_domain:
        return False
    if sender_domain in TRUSTED_DOMAINS:
        return False
    if sender_domain.count("-") >= 2:
        return True
    if any(character.isdigit() for character in sender_domain):
        return True
    if any(keyword in sender_domain for keyword in ["verify", "secure", "login", "alert", "billing", "auth"]):
        return True
    if sender_domain.endswith((".zip", ".click", ".top", ".xyz", ".monster")):
        return True
    return False


def display_name_domain_mismatch(sender_name: str, sender_domain: str) -> bool:
    """Flag display names that imply a major brand from an unrelated domain."""
    lowered_name = sender_name.lower()
    if not lowered_name or not sender_domain:
        return False
    brand_checks = {
        "google": "google.com",
        "microsoft": "microsoft.com",
        "paypal": "paypal.com",
        "amazon": "amazon.com",
        "apple": "apple.com",
        "github": "github.com",
        "linkedin": "linkedin.com",
    }
    for brand, trusted_domain in brand_checks.items():
        if brand in lowered_name and trusted_domain not in sender_domain:
            return True
    return False


def reply_to_mismatch(headers: Dict[str, str], sender_email: str) -> bool:
    """Check whether Reply-To differs from the sender address."""
    reply_to = headers.get("reply-to", "") if headers else ""
    if not reply_to or not sender_email:
        return False
    return sender_email.lower() not in reply_to.lower()


def authentication_header_issues(headers: Dict[str, str]) -> int:
    """Summarize authentication concerns from SPF/DKIM/DMARC-like headers."""
    auth_text = " ".join([headers.get("received-spf", ""), headers.get("authentication-results", "")]).lower()
    issue_count = 0
    for token in ["spf=fail", "spf fail", "dkim=fail", "dmarc=fail", "softfail", "temperror"]:
        if token in auth_text:
            issue_count += 1
    return issue_count


def impersonation_sender_name(sender_name: str) -> bool:
    """Detect generic impersonation-style sender display names."""
    lowered_name = sender_name.lower()
    return any(keyword in lowered_name for keyword in IMPERSONATION_NAMES)


def link_density_flags(link_count: int, body_text: str) -> bool:
    """Flag email bodies that contain too many links for their length."""
    if link_count >= 4:
        return True
    words = max(len(body_text.split()), 1)
    return link_count >= 2 and words < 40


def short_threatening_cta(text: str) -> bool:
    """Detect short call-to-action phrases common in phishing emails."""
    lowered = text.lower()
    return any(phrase in lowered for phrase in SHORT_CTA_PHRASES)


def build_combined_text(email_record: Dict[str, Any]) -> str:
    """Combine normalized email fields into a single analysis string."""
    preprocessed = preprocess_email_fields(
        subject=email_record.get("subject", ""),
        sender_email=email_record.get("sender_email", ""),
        sender_name=email_record.get("sender_name", ""),
        body_text=email_record.get("body_text", ""),
        snippet=email_record.get("snippet", ""),
    )
    return " ".join(
        [
            preprocessed["clean_subject"],
            preprocessed["clean_sender"],
            preprocessed["clean_body_text"],
            preprocessed["clean_snippet"],
        ]
    ).strip()


def handcrafted_features(email_record: Dict[str, Any]) -> Dict[str, Any]:
    """Extract explainable phishing-oriented features from an email record."""
    subject = email_record.get("subject", "") or ""
    body_text = email_record.get("body_text", "") or ""
    snippet = email_record.get("snippet", "") or ""
    sender_name = email_record.get("sender_name", "") or ""
    sender_email = email_record.get("sender_email", "") or ""
    headers = email_record.get("headers", {}) or {}
    combined_raw = f"{subject} {snippet} {body_text}".strip()
    combined_lower = combined_raw.lower()
    sender_domain = extract_domain(sender_email)
    link_count = int(email_record.get("link_count", 0) or len(email_record.get("links", [])))

    urgent_count = count_matches(combined_lower, URGENT_WORDS)
    suspension_count = count_matches(combined_lower, ACCOUNT_SUSPENSION_WORDS)
    password_reset_count = count_matches(combined_lower, PASSWORD_RESET_WORDS)
    prize_count = count_matches(combined_lower, PRIZE_WORDS)
    payment_count = count_matches(combined_lower, PAYMENT_WORDS)
    credential_count = count_matches(combined_lower, SENSITIVE_INFO_WORDS)
    auth_issue_count = authentication_header_issues(headers)
    suspicious_domain_flag = suspicious_sender_domain(sender_domain)
    display_domain_mismatch_flag = display_name_domain_mismatch(sender_name, sender_domain)
    reply_mismatch_flag = reply_to_mismatch(headers, sender_email)
    impersonation_flag = impersonation_sender_name(sender_name)
    link_density_flag = link_density_flags(link_count, body_text)
    cta_flag = short_threatening_cta(combined_lower)

    suspicious_keyword_count = (
        urgent_count
        + suspension_count
        + password_reset_count
        + prize_count
        + payment_count
        + credential_count
    )

    return {
        "combined_text": build_combined_text(email_record),
        "sender_domain": sender_domain,
        "urgent_word_count": urgent_count,
        "account_suspension_count": suspension_count,
        "password_reset_count": password_reset_count,
        "prize_word_count": prize_count,
        "payment_word_count": payment_count,
        "credential_request_count": credential_count,
        "suspicious_keyword_count": suspicious_keyword_count,
        "suspicious_sender_domain": int(suspicious_domain_flag),
        "display_name_domain_mismatch": int(display_domain_mismatch_flag),
        "reply_to_mismatch": int(reply_mismatch_flag),
        "impersonation_sender_name": int(impersonation_flag),
        "auth_issue_count": auth_issue_count,
        "link_count": link_count,
        "too_many_links": int(link_density_flag),
        "uppercase_ratio": uppercase_ratio(combined_raw),
        "number_ratio": number_ratio(combined_raw),
        "special_character_ratio": special_character_ratio(combined_raw),
        "short_cta_flag": int(cta_flag),
        "indicator_tokens": " ".join(
            [
                f"urgent_{urgent_count}",
                f"suspension_{suspension_count}",
                f"pwdreset_{password_reset_count}",
                f"prize_{prize_count}",
                f"payment_{payment_count}",
                f"credential_{credential_count}",
                f"authissues_{auth_issue_count}",
                f"links_{link_count}",
                "flag_suspiciousdomain" if suspicious_domain_flag else "flag_standarddomain",
                "flag_displaymismatch" if display_domain_mismatch_flag else "flag_displayaligned",
                "flag_replymismatch" if reply_mismatch_flag else "flag_replymatch",
                "flag_impersonation" if impersonation_flag else "flag_noimpersonation",
                "flag_manylinks" if link_density_flag else "flag_normallinks",
                "flag_cta" if cta_flag else "flag_nocta",
            ]
        ),
    }


def prepare_feature_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Generate feature columns from a training dataframe."""
    feature_rows: List[Dict[str, Any]] = []
    for row in df.to_dict(orient="records"):
        feature_rows.append(
            handcrafted_features(
                {
                    "subject": row.get("subject", ""),
                    "sender_name": row.get("sender_name", ""),
                    "sender_email": row.get("sender_email", row.get("sender", "")),
                    "body_text": row.get("body_text", row.get("body", "")),
                    "snippet": row.get("snippet", ""),
                    "headers": row.get("headers", {}),
                    "link_count": row.get("link_count", 0),
                    "links": row.get("links", []),
                }
            )
        )

    feature_df = pd.DataFrame(feature_rows)
    output = pd.concat([df.reset_index(drop=True), feature_df], axis=1)
    output["model_text"] = output["combined_text"].fillna("") + " " + output["indicator_tokens"].fillna("")
    return output
