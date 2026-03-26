from __future__ import annotations

from typing import Any, Dict, List

from app.features import handcrafted_features


def build_reason_list(email_record: Dict[str, Any]) -> List[str]:
    """Create human-readable reasons for a phishing prediction."""
    features = handcrafted_features(email_record)
    reasons: List[str] = []

    if features["urgent_word_count"] > 0:
        reasons.append("Urgent or pressure-based language was detected.")
    if features["account_suspension_count"] > 0:
        reasons.append("The email mentions account suspension, locking, or forced verification.")
    if features["password_reset_count"] > 0:
        reasons.append("The message uses password reset or password update language.")
    if features["prize_word_count"] > 0:
        reasons.append("Prize, reward, or lottery language appears in the message.")
    if features["payment_word_count"] > 0:
        reasons.append("The email references payment, invoice, refund, or transfer activity.")
    if features["suspicious_sender_domain"]:
        reasons.append("The sender domain looks suspicious or spoofed.")
    if features["display_name_domain_mismatch"]:
        reasons.append("The display name suggests a known brand, but the sender domain does not match.")
    if features["reply_to_mismatch"]:
        reasons.append("The Reply-To address does not match the sender address.")
    if features["credential_request_count"] > 0:
        reasons.append("The message appears to request passwords or other sensitive information.")
    if features["impersonation_sender_name"]:
        reasons.append("The sender name looks like an impersonated support, admin, or security contact.")
    if features["too_many_links"]:
        reasons.append("The email contains an unusually high number of links for its length.")
    if features["auth_issue_count"] > 0:
        reasons.append("Authentication-related headers indicate SPF, DKIM, or DMARC issues.")
    if features["short_cta_flag"]:
        reasons.append("Short high-pressure call-to-action phrases such as 'verify now' were detected.")
    if features["uppercase_ratio"] > 0.25:
        reasons.append("The message uses an unusually high amount of uppercase text.")
    if features["special_character_ratio"] > 0.08:
        reasons.append("The message contains an unusual amount of special characters.")
    if features["number_ratio"] > 0.08:
        reasons.append("The message contains an unusually high amount of numeric text.")
    if features["suspicious_keyword_count"] >= 3:
        reasons.append("Multiple phishing-related keywords were found in the same email.")

    if not reasons:
        reasons.append("No strong phishing indicators were detected from the content and metadata.")

    return reasons


def risk_badge(score: float) -> str:
    """Map a numeric score to a simple risk category."""
    if score >= 80:
        return "High Risk"
    if score >= 55:
        return "Medium Risk"
    return "Low Risk"
