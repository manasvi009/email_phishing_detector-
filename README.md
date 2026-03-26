# Real-Time Email Phishing Detector for Gmail

This project is a local, production-style Gmail phishing detection system built with Python, Streamlit, Gmail API, and classic machine learning. It connects to a real Gmail mailbox, monitors incoming emails in near real time, parses live messages, scores phishing risk, explains suspicious indicators, optionally applies a Gmail label, and stores scan history locally in SQLite and CSV.

## Problem Statement

Phishing emails often look legitimate enough to bypass casual inspection. This project demonstrates how to build a practical local monitoring tool that watches a Gmail inbox, extracts email content and headers, applies NLP and ML to classify each message as phishing or legitimate, and surfaces explainable risk signals for review.

## Key Features

- Gmail OAuth authentication with secure local token storage
- Live Gmail mailbox access using Gmail API
- Near real-time monitoring with:
  - Gmail watch/history workflow design
  - local polling fallback mode for easy demo use
- Robust email parsing for:
  - sender display name
  - sender email
  - subject
  - snippet
  - plain text and HTML body
  - reply-to
  - return-path
  - SPF/authentication-related headers
- NLP preprocessing:
  - lowercase normalization
  - URL normalization
  - email normalization
  - token cleanup
  - whitespace cleanup
- Feature engineering for phishing indicators such as:
  - urgent language
  - account suspension wording
  - password reset wording
  - payment and invoice wording
  - credential request language
  - suspicious sender domain
  - display-name/domain mismatch
  - reply-to mismatch
  - too many links
  - uppercase, digit, and special-character density
  - short threatening CTA phrases
- ML models:
  - TF-IDF + Logistic Regression
  - TF-IDF + Multinomial Naive Bayes
- Evaluation metrics:
  - accuracy
  - precision
  - recall
  - F1-score
  - confusion matrix
- Explainable suspicious reasons for every email
- Optional Gmail action:
  - apply `Suspected Phishing` label
- Local storage:
  - SQLite history
  - CSV export
  - JSON app state
- Streamlit dashboard for monitoring, review, and export

## Architecture

```text
Gmail Inbox
   |
   v
Gmail API OAuth -> Gmail Reader / Watch / History
   |
   v
Email Parser
   |
   v
Preprocessing + Feature Layer
   |
   v
TF-IDF Vectorizer + ML Classifier
   |
   v
Explainability + Risk Scoring
   |
   +--> Gmail Label Action
   +--> SQLite / CSV / JSON State Storage
   +--> Streamlit Dashboard
```

## Tech Stack

- Python
- Gmail API
- google-api-python-client
- google-auth-oauthlib
- pandas
- numpy
- scikit-learn
- joblib
- python-dotenv
- BeautifulSoup4
- Streamlit
- SQLite

## Project Structure

```text
real-time-email-phishing-detector/
|
├── app/
│   ├── __init__.py
│   ├── actions.py
│   ├── config.py
│   ├── explain.py
│   ├── feature_engineering.py
│   ├── features.py
│   ├── gmail_auth.py
│   ├── gmail_reader.py
│   ├── gmail_watch.py
│   ├── monitor.py
│   ├── parser.py
│   ├── predictor.py
│   ├── preprocess.py
│   ├── storage.py
│   ├── train_model.py
│   └── utils.py
|
├── data/
│   ├── phishing_dataset.csv
│   ├── phishing_emails.csv
│   ├── processed_dataset.csv
│   ├── scan_history.csv
│   ├── scan_history.db
│   └── app_state.json
|
├── model/
│   ├── phishing_model.pkl
│   ├── vectorizer.pkl
│   └── model_metadata.json
|
├── streamlit_app.py
├── requirements.txt
├── .env
├── .env.example
├── README.md
└── credentials.json
```

## Dataset Format

Training expects this format:

```csv
subject,sender,body,label
"Urgent: Verify your account now","security@paypai-alert.com","Dear customer, verify your password immediately to avoid suspension.",1
"Team lunch tomorrow","manager@company.com","Lunch is moved to 1 PM tomorrow in the main cafeteria.",0
```

- `subject`: email subject
- `sender`: sender email address
- `body`: email content
- `label`: `1` for phishing, `0` for legitimate

Starter dataset file:

- `data/phishing_dataset.csv`

## Gmail API Setup

### 1. Create a Google Cloud project

1. Open Google Cloud Console.
2. Create a new project.
3. Enable the Gmail API.

### 2. Configure OAuth consent screen

1. Go to `APIs & Services` -> `OAuth consent screen`.
2. Choose `External`.
3. Fill the app name and basic details.
4. Add your Gmail account as a test user.

### 3. Create OAuth client credentials

1. Go to `APIs & Services` -> `Credentials`.
2. Click `Create Credentials` -> `OAuth client ID`.
3. Choose `Desktop app`.
4. Download the JSON file.
5. Rename it to `credentials.json`.
6. Place it in the project root.

### 4. Optional Gmail watch setup

For production-style watch mode, configure Google Cloud Pub/Sub and set:

- `GMAIL_WATCH_TOPIC_NAME=projects/<project-id>/topics/<topic-name>`

Important:

- Gmail watch mode needs a Pub/Sub topic with correct IAM permissions for Gmail push notifications.
- Local demo users can skip this and use `history` or `polling` mode.

## How Real-Time Monitoring Works

### Watch mode

- The app calls Gmail `users.watch`.
- Gmail publishes mailbox change notifications to your Pub/Sub topic.
- The code stores the latest `historyId`.
- The app then uses Gmail History API to resolve changed message ids.
- Best for production-style architecture.

### History mode

- The app stores the last known `historyId`.
- On every monitor cycle, it calls Gmail History API and retrieves newly added message ids.
- Useful when you want Gmail-native incremental tracking without full Pub/Sub setup.

### Polling fallback mode

- The app checks the most recent inbox emails every X seconds.
- It skips already seen message ids.
- This is the easiest local demo mode.

## Setup Commands

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

## Run Commands

### Train the model

```powershell
python -m app.train_model
```

### Start the Streamlit dashboard

```powershell
streamlit run streamlit_app.py
```

### Open the app

```text
http://localhost:8501
```

## How to Use the App

1. Copy `.env.example` to `.env`.
2. Place `credentials.json` in the project root.
3. Train the model.
4. Launch Streamlit.
5. Click `Connect Gmail`.
6. Complete OAuth consent in the browser.
7. Run `Manual Scan Latest Emails` for an initial test.
8. Choose `polling`, `history`, or `watch` monitoring mode.
9. Click `Start Monitoring`.
10. Review labels, risk scores, suspicious reasons, and parsed email details.

## Streamlit Dashboard Includes

- project title and overview
- Gmail connection status
- model status
- start/stop monitor controls
- manual scan button
- total scanned, suspicious detected, legitimate detected, and last scan time summary cards
- filter options
- chart for phishing vs legitimate counts
- expandable email detail cards
- downloadable CSV results
- monitoring settings for:
  - max emails
  - polling interval
  - monitor mode
  - Gmail label action
  - confidence threshold

## Optional Labeling

If enabled, the app can apply a Gmail label:

- `Suspected Phishing`

The software never auto-deletes emails.

## Safe Testing Notes

- Start with your own inbox and test-only emails.
- Send yourself controlled phishing-like samples from another account.
- Do not use real credentials in test emails.
- Review model decisions manually before trusting label automation.

## Sample Screenshots

Add screenshots later for:

- dashboard home
- Gmail connect flow
- manual scan results
- live monitoring view
- expanded suspicious email card

## Limitations

- Watch mode requires extra Google Cloud Pub/Sub setup.
- Local Streamlit monitoring is near real time, not true background daemon processing.
- Baseline TF-IDF models are practical and fast, but less context-aware than transformer models.
- Sender/domain reputation is heuristic-based and not backed by external threat intelligence.

## Future Improvements

- Add transformer-based classifiers such as DistilBERT
- Add richer header reputation and DMARC parsing
- Add WHOIS/domain age or reputation checks
- Add attachment-aware analysis
- Add analyst feedback loop for false positives and false negatives
- Add SHAP or LIME explainability
- Add service mode with a real background worker
- Add email notification or desktop alerting for high-risk detections

## Notes About `credentials.json`

`credentials.json` is not committed because it contains OAuth client details for your Google Cloud project. You must create and download it yourself.
