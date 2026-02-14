# Lead Mail Agent (Streamlit + FastAPI + Postgres + Gmail + LangGraph)

This project provides a full-stack starter for:
- User login
- Gmail OAuth connect
- Triggered AI-agent style email triage (latest 5-10 emails)
- Forward relevant lead-like emails to a destination mailbox
- Ignore spam-like content
- Send relevant summaries to WhatsApp
- Generate and send reply drafts via Gmail API

## Architecture

- **Frontend**: Streamlit dashboard (`frontend/streamlit_app.py`)
- **Backend API**: FastAPI (`backend/app/main.py`)
- **Database**: Postgres via SQLAlchemy models (`User`, `GmailAccount`, `ProcessedEmail`)
- **Agent Workflow**: LangGraph state graph (`backend/app/agents/email_agent.py`)
- **Integrations**:
  - Gmail API (OAuth + read + send)
  - Twilio WhatsApp API

## Setup

1. Create env file:
   ```bash
   cp .env.example .env
   ```

2. Start Postgres:
   ```bash
   docker compose up -d db
   ```

3. Install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. Start FastAPI:
   ```bash
   uvicorn backend.app.main:app --reload --port 8000
   ```

5. Start Streamlit:
   ```bash
   streamlit run frontend/streamlit_app.py --server.port 8501
   ```

## Key Endpoints

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/gmail/connect`
- `GET /auth/gmail/callback`
- `POST /automation/trigger?batch_size=5`
- `POST /automation/reply`

## Triggering Strategy

Use `POST /automation/trigger` as:
- manual webhook trigger,
- or schedule it via cron/cloud scheduler.

Each trigger fetches latest 5-10 Gmail messages and classifies them.

## Production Notes

- Replace keyword-based classifier with an LLM node in LangGraph.
- Persist Gmail credentials encrypted at rest.
- Add token refresh + Gmail watch/pubsub webhook for near real-time processing.
- Add proper user-to-WhatsApp mapping and approval workflow for sending auto-replies.
