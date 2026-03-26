from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB

from app.config import AppConfig, get_config
from app.features import prepare_feature_dataframe


def train_and_save_model(
    dataset_path: str | Path | None = None,
    config: AppConfig | None = None,
) -> dict:
    """Train phishing classifiers, compare them, and save the best artifacts."""
    active_config = config or get_config()
    active_config.ensure_directories()
    dataset_path = Path(dataset_path or active_config.dataset_path)

    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    df = pd.read_csv(dataset_path)
    required_columns = {"subject", "sender", "body", "label"}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing_columns)}")

    df = df.rename(columns={"sender": "sender_email", "body": "body_text"})
    processed_df = prepare_feature_dataframe(df)

    x_train, x_test, y_train, y_test = train_test_split(
        processed_df["model_text"],
        processed_df["label"],
        test_size=0.25,
        random_state=42,
        stratify=processed_df["label"],
    )

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_df=0.95, sublinear_tf=True)
    x_train_vectorized = vectorizer.fit_transform(x_train)
    x_test_vectorized = vectorizer.transform(x_test)

    candidate_models = {
        "logistic_regression": LogisticRegression(max_iter=2000, class_weight="balanced"),
        "multinomial_nb": MultinomialNB(),
    }

    results = {}
    best_model_name = ""
    best_model = None
    best_f1 = -1.0

    for model_name, model in candidate_models.items():
        model.fit(x_train_vectorized, y_train)
        predictions = model.predict(x_test_vectorized)
        metrics = {
            "accuracy": round(accuracy_score(y_test, predictions), 4),
            "precision": round(precision_score(y_test, predictions), 4),
            "recall": round(recall_score(y_test, predictions), 4),
            "f1_score": round(f1_score(y_test, predictions), 4),
            "confusion_matrix": confusion_matrix(y_test, predictions).tolist(),
            "classification_report": classification_report(y_test, predictions, digits=4),
        }
        results[model_name] = metrics

        if metrics["f1_score"] > best_f1:
            best_f1 = metrics["f1_score"]
            best_model_name = model_name
            best_model = model

    if best_model is None:
        raise RuntimeError("Model training failed to produce a best model.")

    joblib.dump(best_model, active_config.model_path)
    joblib.dump(vectorizer, active_config.vectorizer_path)
    processed_df.to_csv(active_config.processed_dataset_path, index=False)

    metadata = {
        "best_model_name": best_model_name,
        "dataset_path": str(dataset_path),
        "train_size": int(len(x_train)),
        "test_size": int(len(x_test)),
        "vectorizer": {
            "ngram_range": [1, 2],
            "sublinear_tf": True,
            "max_df": 0.95,
        },
        "model_results": results,
    }
    active_config.metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


if __name__ == "__main__":
    training_summary = train_and_save_model()
    print("\nModel training completed.")
    print(f"Best model: {training_summary['best_model_name']}")
    for model_name, metrics in training_summary["model_results"].items():
        print(f"\n{model_name}")
        print(f"Accuracy : {metrics['accuracy']}")
        print(f"Precision: {metrics['precision']}")
        print(f"Recall   : {metrics['recall']}")
        print(f"F1-score : {metrics['f1_score']}")
        print(f"Confusion: {metrics['confusion_matrix']}")
