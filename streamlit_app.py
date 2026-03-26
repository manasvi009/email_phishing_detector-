from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from app.config import get_config, get_setup_status
from app.gmail_auth import get_gmail_service
from app.monitor import MonitorSettings, run_manual_scan, run_monitor_cycle, start_monitoring, stop_monitoring
from app.storage import initialize_storage, load_app_state, load_scan_history
from app.train_model import train_and_save_model
from app.utils import export_dataframe, load_json


st.set_page_config(page_title="Real-Time Email Phishing Detector", page_icon="shield", layout="wide")


def initialize_session_state() -> None:
    """Create Streamlit session keys used by the dashboard."""
    defaults: dict[str, Any] = {
        "gmail_service": None,
        "monitor_status": "Monitor is idle.",
        "connection_status": "Not connected",
        "results_df": pd.DataFrame(),
        "last_monitor_cycle_count": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def apply_custom_styles() -> None:
    """Inject dashboard styles."""
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(14, 116, 144, 0.14), transparent 28%),
                radial-gradient(circle at bottom right, rgba(245, 158, 11, 0.14), transparent 26%),
                linear-gradient(180deg, #f8fafc 0%, #eff6ff 100%);
        }
        .hero {
            padding: 1.4rem 1.6rem;
            border-radius: 22px;
            background: linear-gradient(135deg, #0f172a 0%, #164e63 55%, #155e75 100%);
            color: white;
            box-shadow: 0 18px 44px rgba(15, 23, 42, 0.16);
            margin-bottom: 1rem;
        }
        .metric-card {
            border-radius: 18px;
            padding: 1rem 1.1rem;
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(15, 23, 42, 0.08);
            box-shadow: 0 10px 28px rgba(15, 23, 42, 0.05);
        }
        .email-card {
            background: rgba(255, 255, 255, 0.94);
            border-radius: 18px;
            padding: 1rem;
            border: 1px solid rgba(15, 23, 42, 0.08);
            box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
            margin-bottom: 0.8rem;
        }
        .risk-pill {
            display: inline-block;
            padding: 0.28rem 0.7rem;
            border-radius: 999px;
            font-size: 0.82rem;
            font-weight: 700;
        }
        .risk-high { background: #fee2e2; color: #991b1b; }
        .risk-medium { background: #fef3c7; color: #92400e; }
        .risk-low { background: #dcfce7; color: #166534; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    """Render the dashboard hero section."""
    st.markdown(
        """
        <div class="hero">
            <h1>Real-Time Email Phishing Detector for Gmail</h1>
            <p>Authenticate with Gmail, monitor new inbox activity in near real time, classify phishing risk with NLP + ML, and review explainable detections in one local dashboard.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_setup_panel(config) -> dict[str, bool]:
    """Show a project readiness checklist so missing setup is obvious."""
    setup_status = get_setup_status(config)
    with st.expander("Project Setup Checklist", expanded=not setup_status["credentials_exists"]):
        st.write("Local requirements:")
        st.write(f"- Dataset: {'Ready' if setup_status['dataset_exists'] else 'Missing'}")
        st.write(f"- Trained model: {'Ready' if setup_status['model_exists'] else 'Missing'}")
        st.write(f"- Vectorizer: {'Ready' if setup_status['vectorizer_exists'] else 'Missing'}")
        st.write(f"- Model metadata: {'Ready' if setup_status['metadata_exists'] else 'Missing'}")
        st.write(f"- Gmail OAuth credentials: {'Ready' if setup_status['credentials_exists'] else 'Missing'}")
        st.write(f"- Gmail token: {'Ready' if setup_status['token_exists'] else 'Not created yet'}")
        st.write(f"- Watch mode Pub/Sub topic: {'Configured' if setup_status['watch_configured'] else 'Not configured'}")

        if not setup_status["credentials_exists"]:
            st.warning(
                "Gmail OAuth credentials are missing. Download your Desktop OAuth client JSON from Google Cloud "
                f"and place it here: `{config.credentials_path}`"
            )
        elif not setup_status["token_exists"]:
            st.info("OAuth token is not created yet. It will be generated automatically the first time you connect Gmail.")

    return setup_status


def get_service():
    """Return a cached Gmail service for the current session."""
    service = st.session_state.get("gmail_service")
    if service is None:
        service = get_gmail_service()
        st.session_state["gmail_service"] = service
    st.session_state["connection_status"] = "Connected to Gmail"
    return service


def load_results_into_session() -> pd.DataFrame:
    """Load persisted scan history into Streamlit state."""
    results_df = load_scan_history(limit=250)
    st.session_state["results_df"] = results_df
    return results_df


def filter_results(results_df: pd.DataFrame, filter_option: str) -> pd.DataFrame:
    """Filter displayed scan results by label."""
    if results_df.empty:
        return results_df
    if filter_option == "Phishing only":
        return results_df[results_df["label"] == "Phishing"]
    if filter_option == "Legitimate only":
        return results_df[results_df["label"] == "Legitimate"]
    return results_df


def risk_class_name(risk_badge_value: str) -> str:
    """Map a risk badge to its CSS class."""
    if risk_badge_value == "High Risk":
        return "risk-high"
    if risk_badge_value == "Medium Risk":
        return "risk-medium"
    return "risk-low"


def show_training_status() -> None:
    """Display the current model metadata."""
    config = get_config()
    metadata = load_json(config.metadata_path, default={})
    if not metadata:
        st.info("No trained model found yet. Train the model from the sidebar before monitoring live Gmail emails.")
        return

    best_model_name = metadata.get("best_model_name", "unknown")
    metrics = metadata.get("model_results", {}).get(best_model_name, {})
    cols = st.columns(4)
    items = [
        ("Best Model", best_model_name.replace("_", " ").title()),
        ("Accuracy", metrics.get("accuracy", "N/A")),
        ("Recall", metrics.get("recall", "N/A")),
        ("F1 Score", metrics.get("f1_score", "N/A")),
    ]
    for col, (label, value) in zip(cols, items):
        with col:
            st.markdown(
                f"<div class='metric-card'><strong>{label}</strong><br><span style='font-size:1.35rem'>{value}</span></div>",
                unsafe_allow_html=True,
            )


def render_summary_cards(results_df: pd.DataFrame, app_state: dict[str, Any]) -> None:
    """Render top-level monitoring summary cards."""
    total_scanned = len(results_df)
    phishing_count = int((results_df["label"] == "Phishing").sum()) if not results_df.empty else 0
    legitimate_count = int((results_df["label"] == "Legitimate").sum()) if not results_df.empty else 0
    last_scan_time = app_state.get("last_scan_time", "Not yet scanned")

    for col, (label, value) in zip(
        st.columns(4),
        [
            ("Total Scanned", total_scanned),
            ("Suspicious Detected", phishing_count),
            ("Legitimate Detected", legitimate_count),
            ("Last Scan Time", last_scan_time),
        ],
    ):
        with col:
            st.markdown(
                f"<div class='metric-card'><strong>{label}</strong><br><span style='font-size:1.35rem'>{value}</span></div>",
                unsafe_allow_html=True,
            )


def render_result_cards(results_df: pd.DataFrame) -> None:
    """Render each email result as a card."""
    for _, row in results_df.iterrows():
        pill_class = risk_class_name(row["risk_badge"])
        st.markdown(
            f"""
            <div class="email-card">
                <div style="display:flex; justify-content:space-between; gap:1rem; align-items:flex-start;">
                    <div>
                        <h4 style="margin:0 0 0.35rem 0;">{row['subject'] or '(No Subject)'}</h4>
                        <div><strong>{row['sender_name'] or 'Unknown Sender'}</strong> &lt;{row['sender_email'] or 'unknown'}&gt;</div>
                        <div style="color:#475569; margin-top:0.3rem;">{row['preview']}</div>
                    </div>
                    <div style="text-align:right;">
                        <span class="risk-pill {pill_class}">{row['risk_badge']}</span>
                        <div style="margin-top:0.45rem; font-size:1.5rem; font-weight:800;">{row['risk_score']}%</div>
                        <div style="color:#475569;">{row['label']}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.progress(min(max(float(row["risk_score"]) / 100, 0.0), 1.0), text=f"Confidence: {row['confidence']}%")
        st.caption(
            f"Date: {row.get('date', 'Unknown')} | Model: {row.get('model_name', 'unknown')} | Mode: {row.get('monitor_mode', 'n/a')}"
        )
        with st.expander("View parsed email details"):
            st.write("Reasons:")
            for reason in row["reasons"]:
                st.write(f"- {reason}")
            st.write("Headers:")
            st.json(row["headers"])
            st.write("Body:")
            st.write(row["body_text"] or "No readable body text found.")


def render_live_fragment(settings: MonitorSettings, poll_interval_seconds: int) -> None:
    """Run the auto-refresh monitor loop while monitoring is active."""
    app_state = load_app_state()
    if not app_state.get("monitor_running", False):
        return

    @st.fragment(run_every=f"{poll_interval_seconds}s")
    def live_monitor_fragment() -> None:
        try:
            service = get_service()
            previous_total = len(st.session_state.get("results_df", pd.DataFrame()))
            cycle_result = run_monitor_cycle(service=service, settings=settings)
            st.session_state["monitor_status"] = cycle_result.status_message
            st.session_state["last_monitor_cycle_count"] = cycle_result.new_email_count
            updated_results = load_results_into_session()
            if len(updated_results) != previous_total or cycle_result.new_email_count > 0:
                st.rerun()
        except Exception as error:  # noqa: BLE001
            st.session_state["monitor_status"] = f"Monitoring error: {error}"
            st.error(f"Monitor cycle failed: {error}")

    live_monitor_fragment()


def main() -> None:
    """Run the Streamlit dashboard."""
    config = get_config()
    initialize_storage(config)
    initialize_session_state()
    apply_custom_styles()
    render_header()
    show_training_status()
    setup_status = render_setup_panel(config)

    if st.session_state.get("results_df", pd.DataFrame()).empty:
        load_results_into_session()

    app_state = load_app_state(config)

    with st.sidebar:
        st.header("Settings")
        max_emails = st.slider("Number of emails to fetch", min_value=5, max_value=50, value=config.max_email_fetch, step=5)
        gmail_query = st.text_input("Gmail query", value=config.default_gmail_query)
        poll_interval_seconds = st.slider(
            "Polling interval (seconds)",
            min_value=15,
            max_value=300,
            value=config.polling_interval_seconds,
            step=15,
        )
        confidence_threshold = st.slider(
            "Confidence threshold",
            min_value=0.50,
            max_value=0.95,
            value=float(config.confidence_threshold),
            step=0.05,
        )
        monitor_mode = st.selectbox(
            "Monitoring mode",
            options=["polling", "history", "watch"],
            index=0 if app_state.get("monitor_mode", "polling") == "polling" else ["polling", "history", "watch"].index(app_state.get("monitor_mode", "polling")),
            help="Use watch/history for a production-style Gmail workflow. Polling is the simplest local fallback.",
        )
        apply_gmail_label = st.checkbox("Apply Gmail label to phishing emails", value=config.apply_gmail_label_by_default)
        filter_option = st.radio("Result filter", ["Show all", "Phishing only", "Legitimate only"])
        train_clicked = st.button("Train / Re-train Model", use_container_width=True)
        connect_clicked = st.button("Connect Gmail", use_container_width=True, disabled=not setup_status["credentials_exists"])
        manual_scan_clicked = st.button(
            "Manual Scan Latest Emails",
            type="primary",
            use_container_width=True,
            disabled=not setup_status["credentials_exists"],
        )
        start_monitor_clicked = st.button(
            "Start Monitoring",
            use_container_width=True,
            disabled=not setup_status["credentials_exists"],
        )
        stop_monitor_clicked = st.button("Stop Monitoring", use_container_width=True, disabled=not app_state.get("monitor_running", False))

        if not setup_status["credentials_exists"]:
            st.caption("Add `credentials.json` first, then Gmail connect and monitoring buttons will be enabled.")

    settings = MonitorSettings(
        gmail_query=gmail_query,
        max_emails=max_emails,
        confidence_threshold=float(confidence_threshold),
        apply_gmail_label=apply_gmail_label,
        monitor_mode=monitor_mode,
    )

    if train_clicked:
        with st.spinner("Training phishing detection model..."):
            metadata = train_and_save_model(config=config)
        st.success(f"Training complete. Best model: {metadata['best_model_name']}")
        st.rerun()

    if connect_clicked:
        try:
            with st.spinner("Connecting to Gmail..."):
                get_service()
            st.success("Connected to Gmail successfully.")
        except Exception as error:  # noqa: BLE001
            st.session_state["connection_status"] = f"Connection failed: {error}"
            st.error(f"Gmail connection failed: {error}")

    if manual_scan_clicked:
        try:
            with st.spinner("Scanning recent Gmail emails..."):
                service = get_service()
                scan_result = run_manual_scan(service=service, settings=settings, config=config)
                st.session_state["monitor_status"] = scan_result.status_message
                st.session_state["last_monitor_cycle_count"] = scan_result.new_email_count
                load_results_into_session()
            st.success(scan_result.status_message)
        except Exception as error:  # noqa: BLE001
            st.error(f"Manual scan failed: {error}")

    if start_monitor_clicked:
        try:
            with st.spinner("Starting Gmail monitor..."):
                service = get_service()
                start_monitoring(service=service, settings=settings, config=config)
                st.session_state["monitor_status"] = f"Monitoring started in {monitor_mode} mode."
            st.rerun()
        except Exception as error:  # noqa: BLE001
            st.error(f"Could not start monitoring: {error}")

    if stop_monitor_clicked:
        stop_monitoring(config=config)
        st.session_state["monitor_status"] = "Monitoring stopped."
        st.rerun()

    app_state = load_app_state(config)
    results_df = st.session_state.get("results_df", pd.DataFrame())

    st.markdown("### Monitor Status")
    st.info(st.session_state.get("monitor_status", "Monitor is idle."))
    st.caption(
        f"Gmail: {st.session_state.get('connection_status', 'Not connected')} | "
        f"Mode: {app_state.get('monitor_mode', 'polling')} | "
        f"Last scan: {app_state.get('last_scan_time', 'Not yet scanned')} | "
        f"Last error: {app_state.get('last_error', 'None') or 'None'}"
    )
    if not setup_status["credentials_exists"]:
        st.error(
            "Gmail integration is blocked because `credentials.json` is missing. "
            f"Add it at `{config.credentials_path}` to enable inbox scanning."
        )
    if monitor_mode == "watch" and not config.watch_topic_name:
        st.warning("Watch mode requires `GMAIL_WATCH_TOPIC_NAME` in your environment. Until that is configured, use history or polling mode.")

    render_summary_cards(results_df, app_state)

    st.markdown("### Detection Overview")
    if results_df.empty:
        st.info("No scan history yet. Connect Gmail and run a manual scan or start monitoring.")
    else:
        chart_df = results_df["label"].value_counts().rename_axis("label").reset_index(name="count")
        st.bar_chart(chart_df.set_index("label"))

    st.download_button(
        label="Download scan results as CSV",
        data=export_dataframe(results_df.drop(columns=["headers", "body_text"], errors="ignore")) if not results_df.empty else b"",
        file_name="gmail_phishing_scan_results.csv",
        mime="text/csv",
        disabled=results_df.empty,
    )

    st.markdown("### Scan Results")
    filtered_df = filter_results(results_df, filter_option)
    if filtered_df.empty:
        st.info("No emails match the selected filter.")
    else:
        render_result_cards(filtered_df)

    render_live_fragment(settings=settings, poll_interval_seconds=poll_interval_seconds)


if __name__ == "__main__":
    main()
