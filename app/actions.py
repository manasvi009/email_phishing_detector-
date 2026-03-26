from __future__ import annotations

import pandas as pd

from app.config import AppConfig, get_config


def ensure_gmail_label(service, label_name: str) -> str:
    """Create the Gmail label if needed and return its id."""
    labels = service.users().labels().list(userId="me").execute().get("labels", [])
    for label in labels:
        if label.get("name", "").lower() == label_name.lower():
            return label["id"]

    created = (
        service.users()
        .labels()
        .create(
            userId="me",
            body={
                "name": label_name,
                "labelListVisibility": "labelShow",
                "messageListVisibility": "show",
            },
        )
        .execute()
    )
    return created["id"]


def apply_label_to_message(service, message_id: str, label_name: str) -> None:
    """Apply a Gmail label to a single message."""
    label_id = ensure_gmail_label(service, label_name)
    service.users().messages().modify(
        userId="me",
        id=message_id,
        body={"addLabelIds": [label_id]},
    ).execute()


def apply_actions_to_results(
    results_df: pd.DataFrame,
    service,
    apply_gmail_label: bool,
    config: AppConfig | None = None,
) -> pd.DataFrame:
    """Run optional actions such as Gmail labeling for phishing results."""
    active_config = config or get_config()
    if results_df.empty or service is None or not apply_gmail_label:
        return results_df

    updated_df = results_df.copy()
    phishing_rows = updated_df[(updated_df["label"] == "Phishing") & (~updated_df["label_applied"])]
    for index, row in phishing_rows.iterrows():
        try:
            apply_label_to_message(service, row["message_id"], active_config.phishing_label_name)
            updated_df.at[index, "label_applied"] = True
        except Exception:
            updated_df.at[index, "label_applied"] = False

    return updated_df
