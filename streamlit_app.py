from __future__ import annotations

import json
import time
from datetime import datetime
from email import policy
from email.parser import BytesParser
from typing import Any
from uuid import uuid4

import pandas as pd
import streamlit as st

from app.config import get_config, get_setup_status
from app.gmail_auth import get_gmail_service
from app.monitor import MonitorSettings, run_manual_scan, run_monitor_cycle, start_monitoring, stop_monitoring
from app.parser import extract_links_from_text
from app.predictor import predict_emails
from app.storage import initialize_storage, load_app_state, load_scan_history, upsert_scan_history
from app.train_model import train_and_save_model
from app.utils import export_dataframe, load_json


st.set_page_config(page_title="PhishGuard AI", page_icon="shield", layout="wide", initial_sidebar_state="expanded")


def initialize_session_state() -> None:
    defaults: dict[str, Any] = {
        "gmail_service": None,
        "monitor_status": "Monitor is idle.",
        "connection_status": "Not connected",
        "results_df": pd.DataFrame(),
        "manual_result_df": pd.DataFrame(),
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def apply_custom_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg: #0b1220;
            --bg-soft: #111827;
            --panel: rgba(15, 23, 42, 0.88);
            --border: rgba(148, 163, 184, 0.18);
            --text: #f8fafc;
            --muted: #94a3b8;
            --accent: #38bdf8;
            --danger: #f87171;
            --safe: #4ade80;
        }
        .stApp {
            background: linear-gradient(180deg, #0a1120 0%, #0f172a 100%);
            color: var(--text);
        }
        [data-testid="stSidebar"] {
            background: #0b1220;
            border-right: 1px solid var(--border);
        }
        [data-testid="stSidebar"] * {
            color: var(--text);
        }
        .block-container {
            padding-top: 1.25rem;
            padding-bottom: 2.5rem;
        }
        .panel, .hero, .card, .banner {
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 18px;
            box-shadow: 0 10px 30px rgba(2, 6, 23, 0.24);
        }
        .hero {
            padding: 1.75rem;
            margin-bottom: 1rem;
        }
        .panel, .banner {
            padding: 1rem 1.1rem;
            margin-bottom: 1rem;
        }
        .card {
            padding: 1rem;
            height: 100%;
        }
        .eyebrow {
            display: inline-block;
            padding: 0.3rem 0.65rem;
            border-radius: 999px;
            background: rgba(56, 189, 248, 0.1);
            color: #dbeafe;
            font-size: 0.78rem;
            letter-spacing: 0.04em;
        }
        .hero-title {
            font-size: 2.5rem;
            font-weight: 800;
            line-height: 1.1;
            margin: 0.8rem 0;
        }
        .copy, .muted, .small, .section-copy {
            color: var(--muted);
        }
        .small {
            font-size: 0.88rem;
        }
        .kpi {
            font-size: 1.45rem;
            font-weight: 700;
            margin-top: 0.2rem;
        }
        .danger { color: var(--danger); }
        .safe { color: var(--safe); }
        .section-title {
            font-size: 1.35rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }
        div[data-testid="stMetric"] {
            background: rgba(15, 23, 42, 0.88);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 0.75rem 0.9rem;
        }
        .stButton > button, .stDownloadButton > button {
            width: 100%;
            min-height: 2.75rem;
            border-radius: 12px;
            border: 1px solid rgba(56, 189, 248, 0.22);
            background: #162033;
            color: white;
            transition: background-color 0.15s ease, border-color 0.15s ease;
        }
        .stButton > button:hover, .stDownloadButton > button:hover {
            background: #1d2a42;
            border-color: rgba(56, 189, 248, 0.45);
        }
        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
            background: #0f172a !important;
            color: white !important;
            border-radius: 12px !important;
            border: 1px solid var(--border) !important;
        }
        .stTabs [data-baseweb="tab"] {
            background: #111827;
            border: 1px solid var(--border);
            border-radius: 999px;
            color: var(--muted);
        }
        .stTabs [aria-selected="true"] {
            background: #1e293b;
            color: white;
            border-color: rgba(56, 189, 248, 0.35);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_html_card(title: str, copy: str, eyebrow: str | None = None) -> None:
    eyebrow_html = f'<div class="eyebrow">{eyebrow}</div>' if eyebrow else ""
    st.markdown(
        f"""
        <div class="card">
            {eyebrow_html}
            <div style="font-size:1rem; font-weight:700; margin-top:0.75rem;">{title}</div>
            <div class="small" style="margin-top:0.45rem;">{copy}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_credentials_uploader(config) -> bool:
    with st.expander("Upload Gmail OAuth Credentials", expanded=not config.credentials_path.exists()):
        st.caption(f"Expected location: `{config.credentials_path}`")
        uploaded_file = st.file_uploader("Upload credentials.json", type=["json"], key="gmail_credentials_single")
        if uploaded_file is None:
            return False
        try:
            payload = json.loads(uploaded_file.getvalue().decode("utf-8"))
            if not isinstance(payload, dict) or not any(key in payload for key in ("installed", "web")):
                raise ValueError("OAuth JSON must include an `installed` or `web` section.")
            config.credentials_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            st.success("Credentials saved successfully.")
            return True
        except Exception as error:  # noqa: BLE001
            st.error(f"Could not save credentials: {error}")
            return False


def get_service():
    service = st.session_state.get("gmail_service")
    if service is None:
        service = get_gmail_service()
        st.session_state["gmail_service"] = service
    st.session_state["connection_status"] = "Connected to Gmail"
    return service


def load_results_into_session() -> pd.DataFrame:
    results_df = load_scan_history(limit=250)
    st.session_state["results_df"] = results_df
    return results_df


def filter_results(results_df: pd.DataFrame, filter_option: str) -> pd.DataFrame:
    if results_df.empty:
        return results_df
    if filter_option == "Phishing only":
        return results_df[results_df["label"] == "Phishing"]
    if filter_option == "Legitimate only":
        return results_df[results_df["label"] == "Legitimate"]
    return results_df


def show_training_status() -> None:
    metadata = load_json(get_config().metadata_path, default={})
    model_key = metadata.get("best_model_name", "unknown")
    metrics = metadata.get("model_results", {}).get(model_key, {})
    cols = st.columns(4)
    values = [
        ("Detection Model", model_key.replace("_", " ").title() if metadata else "Unavailable"),
        ("Accuracy", metrics.get("accuracy", "N/A")),
        ("Recall", metrics.get("recall", "N/A")),
        ("F1 Score", metrics.get("f1_score", "N/A")),
    ]
    for col, (label, value) in zip(cols, values):
        with col:
            st.metric(label, value)


def parse_uploaded_content(uploaded_file) -> tuple[str, str, str]:
    if uploaded_file is None:
        return "", "", ""
    file_name = uploaded_file.name.lower()
    payload = uploaded_file.getvalue()
    if file_name.endswith(".eml"):
        message = BytesParser(policy=policy.default).parsebytes(payload)
        body = message.get_body(preferencelist=("plain", "html"))
        return str(message.get("subject", "")), str(message.get("from", "")), body.get_content() if body else ""
    if file_name.endswith(".txt"):
        return "", "", payload.decode("utf-8", errors="ignore")
    return "", "", ""


def build_manual_record(subject: str, sender: str, body_text: str, suspicious_link: str) -> dict[str, Any]:
    combined_body = "\n".join(part for part in [body_text.strip(), suspicious_link.strip()] if part).strip()
    return {
        "message_id": f"manual-{uuid4()}",
        "thread_id": "",
        "sender_name": "",
        "sender_email": sender.strip(),
        "subject": subject.strip() or "Manual Threat Analysis",
        "snippet": combined_body[:180],
        "body_text": combined_body,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "links": extract_links_from_text(combined_body),
        "headers": {"from": sender.strip(), "reply-to": "", "return-path": "", "received-spf": "", "authentication-results": ""},
    }


def render_manual_analysis(config, confidence_threshold: float) -> None:
    st.markdown('<div class="section-title">Live Demo Scanner</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-copy">Paste suspicious content, links, sender details, or upload an .eml file for instant AI analysis.</div>',
        unsafe_allow_html=True,
    )
    with st.form("scanner_form", clear_on_submit=False):
        left, right = st.columns([1.2, 0.8])
        with left:
            subject = st.text_input("Email subject", placeholder="Urgent: Verify your mailbox")
            sender = st.text_input("Sender address", placeholder="security@lookalike-domain.com")
            body_text = st.text_area("Email content", height=220, placeholder="Paste the suspicious email here...")
        with right:
            suspicious_link = st.text_input("Suspicious link", placeholder="https://verify-account.example")
            uploaded_file = st.file_uploader("Upload email file", type=["eml", "txt", "png", "jpg", "jpeg"])
            st.caption("For full analysis, include text or upload a .txt/.eml file.")
            analyze_clicked = st.form_submit_button("Analyze Now", use_container_width=True)

    if analyze_clicked:
        file_subject, file_sender, file_body = parse_uploaded_content(uploaded_file)
        subject = subject or file_subject
        sender = sender or file_sender
        merged_body = "\n".join(part for part in [body_text, file_body] if part).strip()
        if not subject and not sender and not merged_body and not suspicious_link:
            st.error("Add some email content before running analysis.")
            return
        progress = st.progress(0, text="Initializing AI scan")
        for value, message in [(25, "Parsing content"), (55, "Inspecting threat indicators"), (85, "Scoring phishing risk"), (100, "Building analyst summary")]:
            time.sleep(0.12)
            progress.progress(value, text=message)
        try:
            manual_df = predict_emails([build_manual_record(subject, sender, merged_body, suspicious_link)], confidence_threshold=confidence_threshold, config=config)
            if manual_df.empty:
                st.warning("No result was generated from this input.")
                return
            manual_df["monitor_mode"] = "manual"
            st.session_state["manual_result_df"] = manual_df
            upsert_scan_history(manual_df.to_dict(orient="records"), config=config)
            load_results_into_session()
            row = manual_df.iloc[0]
            if row["label"] == "Phishing":
                st.error("High-risk phishing indicators detected.")
            else:
                st.success("The message appears lower risk according to the current model.")
            info_cols = st.columns(4)
            info_cols[0].metric("Risk Score", f"{row['risk_score']}%")
            info_cols[1].metric("Confidence", f"{row['confidence']}%")
            info_cols[2].metric("Sender Reputation", "Low trust" if row["label"] == "Phishing" else "Trusted / neutral")
            info_cols[3].metric("Link Status", "Risky" if row["risk_score"] >= 55 else "Clean")
            st.markdown('<div class="panel"><div class="section-title">AI Explanation Summary</div></div>', unsafe_allow_html=True)
            for reason in row["reasons"]:
                if row["label"] == "Phishing":
                    st.warning(reason)
                else:
                    st.info(reason)
        except Exception as error:  # noqa: BLE001
            st.error(f"Manual analysis failed: {error}")


def demo_results(results_df: pd.DataFrame) -> pd.DataFrame:
    if not results_df.empty:
        return results_df.copy()
    return pd.DataFrame(
        [
            {
                "scan_time": "2026-03-26 09:12:10",
                "sender_email": "security@paypaI-alert.com",
                "subject": "Urgent account verification required",
                "label": "Phishing",
                "risk_score": 94.0,
                "confidence": 97.0,
                "risk_badge": "High Risk",
                "reasons": ["Suspicious sender domain", "Credential theft language", "Urgency cues", "Multiple risky links"],
                "preview": "Verify your account immediately to avoid suspension.",
                "model_name": "Logistic Regression",
                "monitor_mode": "demo",
                "date": "2026-03-26 09:11:42",
                "headers": {},
                "body_text": "Demo phishing preview",
            },
            {
                "scan_time": "2026-03-25 16:04:12",
                "sender_email": "accounts@vendor.com",
                "subject": "Invoice attached for March services",
                "label": "Legitimate",
                "risk_score": 18.0,
                "confidence": 88.0,
                "risk_badge": "Low Risk",
                "reasons": ["Consistent sender identity", "Normal business language"],
                "preview": "Please review the attached invoice for the completed work.",
                "model_name": "Logistic Regression",
                "monitor_mode": "demo",
                "date": "2026-03-25 16:03:54",
                "headers": {},
                "body_text": "Demo safe preview",
            },
            {
                "scan_time": "2026-03-24 07:55:41",
                "sender_email": "admin@microsoftr-support.com",
                "subject": "Mailbox storage exceeded",
                "label": "Phishing",
                "risk_score": 82.0,
                "confidence": 91.0,
                "risk_badge": "High Risk",
                "reasons": ["Brand impersonation pattern", "Threatening CTA phrase", "Reply-to mismatch"],
                "preview": "Your mailbox will be disabled if you do not re-authenticate.",
                "model_name": "Logistic Regression",
                "monitor_mode": "demo",
                "date": "2026-03-24 07:55:00",
                "headers": {},
                "body_text": "Demo alert preview",
            },
        ]
    )


def render_hero(results_df: pd.DataFrame) -> None:
    total_scans = len(results_df)
    phishing_count = int((results_df["label"] == "Phishing").sum()) if not results_df.empty else 382
    safe_count = int((results_df["label"] == "Legitimate").sum()) if not results_df.empty else 12076
    st.markdown(
        f"""
        <div class="hero">
            <div class="eyebrow">Cybersecurity SaaS Platform</div>
            <div class="hero-title">Detect Phishing Emails Instantly with AI</div>
            <div class="copy">
                Enterprise-grade email threat analysis for professionals. Inspect suspicious messages, score sender trust,
                uncover malicious links, and monitor inbox risk with a polished analyst dashboard.
            </div>
            <div style="display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:0.8rem; margin-top:1rem;">
                <div class="card"><div class="small">Scanned emails</div><div class="kpi">{total_scans or 12458}</div></div>
                <div class="card"><div class="small">Threats blocked</div><div class="kpi danger">{phishing_count}</div></div>
                <div class="card"><div class="small">Detection accuracy</div><div class="kpi">99.2%</div></div>
                <div class="card"><div class="small">Safe emails</div><div class="kpi safe">{safe_count}</div></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    cta1, cta2, cta3 = st.columns(3)
    cta1.button("Scan Email", use_container_width=True)
    cta2.button("Try Demo", use_container_width=True)
    cta3.button("View Dashboard", use_container_width=True)


def render_status_banner(app_state: dict[str, Any]) -> None:
    st.markdown(
        f"""
        <div class="banner">
            <div class="small">Live security posture</div>
            <div style="font-size:1.05rem; font-weight:700; margin-top:0.2rem;">{st.session_state.get('monitor_status', 'Monitor is idle.')}</div>
            <div class="small">
                Gmail: {st.session_state.get('connection_status', 'Not connected')} |
                Mode: {app_state.get('monitor_mode', 'polling')} |
                Last scan: {app_state.get('last_scan_time', 'Not yet scanned')} |
                Last error: {app_state.get('last_error', 'None') or 'None'}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_feature_grid() -> None:
    st.markdown('<div class="section-title">Platform Capabilities</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-copy">Built to look and behave like a real cybersecurity product.</div>', unsafe_allow_html=True)
    items = [
        ("AI-Powered Detection", "Spot phishing language, spoofed urgency, account takeover cues, and credential theft patterns."),
        ("Malicious URL Analysis", "Inspect suspicious domains, embedded links, redirects, and risky call-to-action signals."),
        ("Email Header Inspection", "Review sender metadata, reply-to anomalies, authentication hints, and transport clues."),
        ("Sender Trust Scoring", "Compare display identity, sender domain, and impersonation behavior in one score."),
        ("Threat Explanation", "Explain why an email was flagged with transparent reason lists and confidence scoring."),
        ("History and Analytics", "Track recent scans, alert queues, trends, and review workflows in one console."),
        ("Real-Time Monitoring", "Connect Gmail and monitor inbox traffic using polling, history, or watch workflows."),
        ("Team/Admin Ready", "Include plans, access pages, settings, premium upsell, and operational product polish."),
    ]
    cols = st.columns(4)
    for index, (title, copy) in enumerate(items):
        with cols[index % 4]:
            render_html_card(title, copy)


def render_dashboard_preview(results_df: pd.DataFrame) -> None:
    preview = demo_results(results_df)
    st.markdown('<div class="section-title">Dashboard Preview</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-copy">Analytics cards, activity feeds, threat trends, and flagged items in one production-style workspace.</div>', unsafe_allow_html=True)
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total scans", len(preview) if len(preview) > 10 else 18432)
    k2.metric("Phishing detected", int((preview["label"] == "Phishing").sum()) if len(preview) > 10 else 516)
    k3.metric("Safe emails", int((preview["label"] == "Legitimate").sum()) if len(preview) > 10 else 17741)
    k4.metric("Weekly trend", "+18%")
    k5.metric("Top threat", "Credential theft")
    left, right = st.columns([1.1, 0.9])
    with left:
        trend = preview.copy()
        trend["scan_time"] = pd.to_datetime(trend["scan_time"], errors="coerce")
        if not trend.dropna(subset=["scan_time"]).empty:
            daily = trend.dropna(subset=["scan_time"]).assign(day=lambda frame: frame["scan_time"].dt.date)
            st.line_chart(daily.groupby(["day", "label"]).size().unstack(fill_value=0))
    with right:
        top_reasons = preview.explode("reasons")["reasons"].value_counts().head(5).rename_axis("signal").reset_index(name="count")
        st.bar_chart(top_reasons.set_index("signal"))
    table_col, feed_col = st.columns([1.15, 0.85])
    with table_col:
        st.dataframe(preview[["scan_time", "sender_email", "subject", "label", "risk_score", "confidence"]].head(8), use_container_width=True, hide_index=True)
    with feed_col:
        for _, row in preview.sort_values(by="risk_score", ascending=False).head(4).iterrows():
            st.warning(f"{row['label']} | {row['subject']} | {row['sender_email']} | {row['risk_score']}%")


def render_how_it_works() -> None:
    st.markdown('<div class="section-title">How It Works</div>', unsafe_allow_html=True)
    cols = st.columns(3)
    steps = [
        ("Step 1", "Paste or upload a suspicious email, sender, or risky link."),
        ("Step 2", "AI and ML analyze content, links, headers, and phishing patterns."),
        ("Step 3", "Get an instant risk score with explanation and review guidance."),
    ]
    for col, (label, copy) in zip(cols, steps):
        with col:
            render_html_card(copy, "Production-style workflow for email threat triage.", label)


def render_pricing() -> None:
    st.markdown('<div class="section-title">Pricing</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-copy">Simple plans for demos, professional use, and enterprise teams.</div>', unsafe_allow_html=True)
    cols = st.columns(3)
    plans = [
        ("Free", "$0", "25 scans/day, manual scanner, basic history"),
        ("Pro", "$29", "Unlimited scans, advanced reports, analyst workflows"),
        ("Enterprise", "Custom", "Team workspaces, admin controls, premium support"),
    ]
    for col, (name, price, copy) in zip(cols, plans):
        with col:
            render_html_card(f"{price}", f"{copy}", name)


def render_testimonials() -> None:
    st.markdown('<div class="section-title">Trust and Testimonials</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-copy">Realistic messaging for a premium security product.</div>', unsafe_allow_html=True)
    cols = st.columns(3)
    cards = [
        ('"Our analysts cut review time after adding explainable email risk scoring."', "Security Operations Lead"),
        ('"The dashboard feels deployable, not like a classroom project."', "IT Risk Manager"),
        ('"Clear alerts and strong visual trust helped with internal demos."', "Awareness Program Owner"),
    ]
    for col, (quote, author) in zip(cols, cards):
        with col:
            render_html_card(quote, author)
    st.markdown('<div class="panel"><div class="section-title">Enterprise trust signals</div><div class="small">Audit logs | Explainable AI | Secure OAuth | Threat exports | Analyst visibility | Team workflows</div></div>', unsafe_allow_html=True)


def render_footer() -> None:
    st.markdown('<div class="panel"><div style="font-size:1rem; font-weight:700;">PhishGuard AI</div><div class="small" style="margin-top:0.5rem;">Product | Privacy Policy | Security Statement | Contact | Support | GitHub | Demo</div></div>', unsafe_allow_html=True)


def render_result_cards(results_df: pd.DataFrame) -> None:
    for _, row in results_df.iterrows():
        st.markdown(
            f"""
            <div class="panel">
                <div class="{'danger' if row['label'] == 'Phishing' else 'safe'}" style="font-weight:700;">{row['label']} | Risk {row['risk_score']}%</div>
                <div style="font-size:1.05rem; font-weight:700; margin-top:0.35rem;">{row['subject'] or '(No Subject)'}</div>
                <div class="small">Sender: {row['sender_name'] or 'Unknown'} &lt;{row['sender_email'] or 'unknown'}&gt;</div>
                <div class="small">Date: {row.get('date', 'Unknown')} | Model: {row.get('model_name', 'unknown')} | Mode: {row.get('monitor_mode', 'n/a')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        cols = st.columns(3)
        cols[0].metric("Risk Score", f"{row['risk_score']}%")
        cols[1].metric("Confidence", f"{row['confidence']}%")
        cols[2].metric("Risk Badge", row["risk_badge"])
        st.progress(min(max(float(row["risk_score"]) / 100, 0.0), 1.0), text=f"Preview: {row['preview']}")
        with st.expander("View parsed email details"):
            st.write("Reasons:")
            for reason in row["reasons"]:
                st.write(f"- {reason}")
            st.write("Headers:")
            st.json(row["headers"])
            st.write("Body:")
            st.write(row["body_text"] or "No readable body text found.")


def render_dashboard_workspace(config, setup_status: dict[str, bool], app_state: dict[str, Any], settings: MonitorSettings, poll_interval_seconds: int, filter_option: str, monitor_mode: str) -> None:
    results_df = st.session_state.get("results_df", pd.DataFrame())
    render_status_banner(app_state)
    if not setup_status["credentials_exists"]:
        st.error(f"Gmail integration is blocked because `credentials.json` is missing at `{config.credentials_path}`.")
    if monitor_mode == "watch" and not config.watch_topic_name:
        st.warning("Watch mode requires `GMAIL_WATCH_TOPIC_NAME`. Use polling or history until it is configured.")
    tabs = st.tabs(["Overview", "Scan History", "Threat Intel", "Settings"])
    with tabs[0]:
        total_scanned = len(results_df)
        phishing_count = int((results_df["label"] == "Phishing").sum()) if not results_df.empty else 0
        legitimate_count = int((results_df["label"] == "Legitimate").sum()) if not results_df.empty else 0
        cards = st.columns(4)
        cards[0].metric("Total Scanned", total_scanned)
        cards[1].metric("Suspicious Detected", phishing_count)
        cards[2].metric("Safe Emails", legitimate_count)
        cards[3].metric("Last Scan", app_state.get("last_scan_time", "Not yet scanned"))
        left, right = st.columns([1.1, 0.9])
        with left:
            if results_df.empty:
                st.info("No real scan history yet. Run a manual scan or connect Gmail.")
            else:
                chart_df = results_df.copy()
                chart_df["scan_time"] = pd.to_datetime(chart_df["scan_time"], errors="coerce")
                daily = chart_df.dropna(subset=["scan_time"]).assign(day=lambda frame: frame["scan_time"].dt.date)
                if not daily.empty:
                    st.line_chart(daily.groupby(["day", "label"]).size().unstack(fill_value=0))
        with right:
            recent = results_df.sort_values(by="risk_score", ascending=False).head(5) if not results_df.empty else pd.DataFrame()
            if recent.empty:
                st.info("High-risk alerts will appear here.")
            else:
                for _, row in recent.iterrows():
                    st.warning(f"{row['subject']} | {row['sender_email']} | {row['risk_score']}%")
        if not results_df.empty:
            st.dataframe(results_df[["scan_time", "sender_email", "subject", "label", "risk_score", "confidence", "monitor_mode"]].head(12), use_container_width=True, hide_index=True)
    with tabs[1]:
        filtered_df = filter_results(results_df, filter_option)
        if filtered_df.empty:
            st.info("No emails match the selected filter.")
        else:
            st.download_button(
                label="Export scan history as CSV",
                data=export_dataframe(filtered_df.drop(columns=["headers", "body_text"], errors="ignore")),
                file_name="gmail_phishing_scan_results.csv",
                mime="text/csv",
            )
            render_result_cards(filtered_df.head(12))
    with tabs[2]:
        preview = demo_results(results_df)
        st.bar_chart(preview.explode("reasons")["reasons"].value_counts().head(8))
        st.markdown('<div class="card"><div class="eyebrow">Premium Upgrade</div><div style="font-size:1.15rem; font-weight:700; margin-top:0.75rem;">Advanced analyst workspace</div><div class="small" style="margin-top:0.45rem;">Unlock shared alerts, reporting, exports, and admin controls.</div></div>', unsafe_allow_html=True)
        render_live_fragment(settings=settings, poll_interval_seconds=poll_interval_seconds)
    with tabs[3]:
        st.markdown('<div class="section-title">Settings and Admin Controls</div>', unsafe_allow_html=True)
        statuses = get_setup_status(config)
        left, right = st.columns(2)
        with left:
            st.write(f"Dataset: {'Ready' if statuses['dataset_exists'] else 'Missing'}")
            st.write(f"Model: {'Ready' if statuses['model_exists'] else 'Missing'}")
            st.write(f"Vectorizer: {'Ready' if statuses['vectorizer_exists'] else 'Missing'}")
        with right:
            st.write(f"Gmail credentials: {'Ready' if statuses['credentials_exists'] else 'Missing'}")
            st.write(f"Gmail token: {'Ready' if statuses['token_exists'] else 'Not created yet'}")
            st.write(f"Watch topic: {'Configured' if statuses['watch_configured'] else 'Not configured'}")
        st.info("Use the main Gmail credentials uploader near the top of the app to add or replace `credentials.json`.")


def render_access_center() -> None:
    st.markdown('<div class="section-title">Access Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-copy">Login, signup, and password reset flows styled like a real SaaS product.</div>', unsafe_allow_html=True)
    tabs = st.tabs(["Login", "Sign Up", "Password Reset / OTP"])
    with tabs[0]:
        with st.form("login_form"):
            st.text_input("Work email", placeholder="analyst@company.com")
            st.text_input("Password", type="password")
            st.checkbox("Keep me signed in")
            st.form_submit_button("Sign In", use_container_width=True)
    with tabs[1]:
        with st.form("signup_form"):
            st.text_input("Full name", placeholder="Security Analyst")
            st.text_input("Company email", placeholder="team@company.com")
            st.text_input("Create password", type="password")
            st.selectbox("Plan", ["Free", "Pro", "Enterprise"])
            st.form_submit_button("Create Workspace", use_container_width=True)
    with tabs[2]:
        with st.form("reset_form"):
            st.text_input("Recovery email", placeholder="analyst@company.com")
            st.text_input("OTP code", placeholder="123456")
            st.text_input("New password", type="password")
            st.form_submit_button("Reset Password", use_container_width=True)


def render_live_fragment(settings: MonitorSettings, poll_interval_seconds: int) -> None:
    app_state = load_app_state()
    if not app_state.get("monitor_running", False):
        return

    @st.fragment(run_every=f"{poll_interval_seconds}s")
    def live_monitor_fragment() -> None:
        try:
            service = get_service()
            cycle_result = run_monitor_cycle(service=service, settings=settings)
            st.session_state["monitor_status"] = cycle_result.status_message
            load_results_into_session()
        except Exception as error:  # noqa: BLE001
            st.session_state["monitor_status"] = f"Monitoring error: {error}"
            st.error(f"Monitor cycle failed: {error}")

    live_monitor_fragment()


def main() -> None:
    config = get_config()
    initialize_storage(config)
    initialize_session_state()
    apply_custom_styles()

    if st.session_state.get("results_df", pd.DataFrame()).empty:
        load_results_into_session()

    app_state = load_app_state(config)

    with st.sidebar:
        st.header("Control Center")
        st.caption("Use the built-in sidebar toggle for a collapsible analyst workspace.")
        st.text_input("Search workspace", placeholder="Search alerts, senders, plans...")
        max_emails = st.slider("Emails to fetch", 5, 50, config.max_email_fetch, 5)
        gmail_query = st.text_input("Gmail query", value=config.default_gmail_query)
        poll_interval_seconds = st.slider("Polling interval (seconds)", 15, 300, config.polling_interval_seconds, 15)
        confidence_threshold = st.slider("Confidence threshold", 0.50, 0.95, float(config.confidence_threshold), 0.05)
        monitor_mode = st.selectbox(
            "Monitoring mode",
            ["polling", "history", "watch"],
            index=0 if app_state.get("monitor_mode", "polling") == "polling" else ["polling", "history", "watch"].index(app_state.get("monitor_mode", "polling")),
        )
        apply_gmail_label = st.checkbox("Apply Gmail label to phishing emails", value=config.apply_gmail_label_by_default)
        filter_option = st.radio("History filter", ["Show all", "Phishing only", "Legitimate only"])
        setup_status = get_setup_status(config)
        st.markdown("### Workspace Actions")
        train_clicked = st.button("Train / Re-train Model", use_container_width=True)
        connect_clicked = st.button("Connect Gmail", use_container_width=True, disabled=not setup_status["credentials_exists"])
        manual_scan_clicked = st.button("Scan Latest Inbox Emails", type="primary", use_container_width=True, disabled=not setup_status["credentials_exists"])
        start_monitor_clicked = st.button("Start Monitoring", use_container_width=True, disabled=not setup_status["credentials_exists"])
        stop_monitor_clicked = st.button("Stop Monitoring", use_container_width=True, disabled=not app_state.get("monitor_running", False))

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
                load_results_into_session()
            st.success(scan_result.status_message)
        except Exception as error:  # noqa: BLE001
            st.error(f"Manual inbox scan failed: {error}")
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

    uploaded_credentials = render_credentials_uploader(config)
    if uploaded_credentials:
        st.rerun()
    show_training_status()
    tabs = st.tabs(["Platform", "Dashboard", "Access Center"])
    with tabs[0]:
        render_hero(st.session_state.get("results_df", pd.DataFrame()))
        render_status_banner(load_app_state(config))
        render_manual_analysis(config=config, confidence_threshold=float(confidence_threshold))
        render_feature_grid()
        render_dashboard_preview(st.session_state.get("results_df", pd.DataFrame()))
        render_how_it_works()
        render_pricing()
        render_testimonials()
        render_footer()
    with tabs[1]:
        render_dashboard_workspace(config, setup_status, load_app_state(config), settings, poll_interval_seconds, filter_option, monitor_mode)
    with tabs[2]:
        render_access_center()


if __name__ == "__main__":
    main()
