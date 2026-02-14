# Lead Mail Agent (Streamlit + FastAPI + Local Postgres + Gmail + LangGraph)

This project is a local-first starter app for:
- User authentication
- Gmail OAuth connect
- Triggered email triage for latest 5-10 emails
- Lead-like email forwarding to a target mailbox
- Spam-like email ignore path
- WhatsApp notification for relevant leads
- AI-style reply drafting + sending through Gmail API

## Tech Stack

- **Backend**: FastAPI (`backend/app/main.py`)
- **Frontend**: Streamlit (`frontend/streamlit_app.py`)
- **Database**: Local PostgreSQL via SQLAlchemy
- **Agent Flow**: LangGraph (`backend/app/agents/email_agent.py`)
- **External APIs**: Gmail API + Twilio WhatsApp API

---

## 1) Prerequisites (Local machine)

Install these locally:

- Python 3.10+
- PostgreSQL 14+ (running locally)
- A Google Cloud OAuth client (Web application type)
- (Optional) Twilio credentials for WhatsApp notifications

---

## 2) Clone and prepare environment

```bash
git clone <your-repo-url>
cd testrepo
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 3) Setup local PostgreSQL (without Docker)

Use your local `psql` client:

```bash
psql -U postgres
```

Inside Postgres shell:

```sql
CREATE DATABASE lead_mailer;
CREATE USER lead_user WITH PASSWORD 'lead_password';
GRANT ALL PRIVILEGES ON DATABASE lead_mailer TO lead_user;
```

Then set your DB URL accordingly:

```env
DATABASE_URL=postgresql+psycopg2://lead_user:lead_password@localhost:5432/lead_mailer
```

> If you prefer using existing `postgres` user/password, keep the default from `.env.example`.

---

## 4) Configure environment variables

Create env file:

```bash
cp .env.example .env
```

Update at minimum:

- `DATABASE_URL`
- `SECRET_KEY`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REDIRECT_URI` (must match your Google OAuth config, default: `http://localhost:8000/auth/gmail/callback`)
- `FORWARD_TO_EMAIL`

Optional (for WhatsApp):

- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_WHATSAPP_FROM`
- `TWILIO_WHATSAPP_TO`

---

## 5) Run backend locally

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check:

```bash
curl http://localhost:8000/health
```

On startup, tables are auto-created via SQLAlchemy metadata.

---

## 6) Run Streamlit locally

Open another terminal, activate venv, then:

```bash
streamlit run frontend/streamlit_app.py --server.port 8501
```

Open: `http://localhost:8501`

---

## 7) Local usage flow

1. Register or login from Streamlit UI.
2. Click **Get Gmail Connect URL** and complete consent in browser.
3. Trigger email agent with batch size (1-10).
4. Relevant lead-like emails are forwarded to `FORWARD_TO_EMAIL`.
5. If Twilio is configured, a WhatsApp summary is sent.
6. Use reply section to send a drafted response through Gmail API.

---

## API Routes

### Public
- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/gmail/callback` (OAuth provider callback endpoint)

### Protected (Bearer token required)
- `GET /auth/me`
- `GET /auth/gmail/connect`
- `POST /automation/trigger?batch_size=5`
- `POST /automation/reply`

---

## Notes

- The current LangGraph classifier is keyword-based as a starter and can be replaced with an LLM node.
- OAuth state is signed and short-lived to reduce tampering risk.
- For production, add encryption for token storage, refresh-token lifecycle handling, and robust audit logging.
