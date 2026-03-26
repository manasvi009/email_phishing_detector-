from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import joblib
import numpy as np
import pandas as pd

from app.config import AppConfig, get_config
from app.explain import build_reason_list, risk_badge
from app.features import handcrafted_features
from app.utils import load_json, timestamp_now


def load_artifacts(
    config: AppConfig | None = None,
    model_path: Path | None = None,
    vectorizer_path: Path | None = None,
    metadata_path: Path | None = None,
):
    """Load the trained model, vectorizer, and metadata files."""
    active_config = config or get_config()
    model_path = model_path or active_config.model_path
    vectorizer_path = vectorizer_path or active_config.vectorizer_path
    metadata_path = metadata_path or active_config.metadata_path

    if not model_path.exists() or not vectorizer_path.exists():
        raise FileNotFoundError("Model files not found. Run `python -m app.train_model` first.")

    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)
    metadata = load_json(metadata_path, default={})
    return model, vectorizer, metadata


def predict_emails(
    email_records: List[Dict[str, Any]],
    confidence_threshold: float = 0.55,
    config: AppConfig | None = None,
) -> pd.DataFrame:
    """Predict phishing risk for parsed email records."""
    if not email_records:
        return pd.DataFrame()

    model, vectorizer, metadata = load_artifacts(config=config)
    feature_rows = [handcrafted_features(record) for record in email_records]
    feature_df = pd.DataFrame(feature_rows)
    model_text = feature_df["combined_text"].fillna("") + " " + feature_df["indicator_tokens"].fillna("")
    transformed = vectorizer.transform(model_text)

    predictions = model.predict(transformed)
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(transformed)[:, 1]
    else:
        scores = model.decision_function(transformed)
        probabilities = 1 / (1 + np.exp(-scores))

    rows: List[Dict[str, Any]] = []
    for email_record, predicted_label, phishing_probability in zip(email_records, predictions, probabilities):
        normalized_probability = float(phishing_probability)
        model_vote_is_phishing = int(predicted_label) == 1
        is_phishing = model_vote_is_phishing or normalized_probability >= confidence_threshold
        confidence = normalized_probability if is_phishing else 1 - normalized_probability
        risk_score = round(normalized_probability * 100, 2)
        rows.append(
            {
                "scan_time": timestamp_now(),
                "message_id": email_record.get("message_id", ""),
                "thread_id": email_record.get("thread_id", ""),
                "sender_name": email_record.get("sender_name", ""),
                "sender_email": email_record.get("sender_email", ""),
                "subject": email_record.get("subject", ""),
                "date": email_record.get("date", ""),
                "preview": email_record.get("snippet", "") or email_record.get("body_text", "")[:160],
                "label": "Phishing" if is_phishing else "Legitimate",
                "risk_score": risk_score,
                "confidence": round(float(confidence) * 100, 2),
                "risk_badge": risk_badge(risk_score),
                "reasons": build_reason_list(email_record),
                "headers": email_record.get("headers", {}),
                "body_text": email_record.get("body_text", ""),
                "label_applied": False,
                "model_name": metadata.get("best_model_name", "unknown"),
                "phishing_probability": round(normalized_probability, 6),
            }
        )

    return pd.DataFrame(rows).sort_values(by="risk_score", ascending=False).reset_index(drop=True)
