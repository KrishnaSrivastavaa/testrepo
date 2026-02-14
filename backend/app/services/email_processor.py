from sqlalchemy.orm import Session

from ..agents.email_agent import email_agent
from ..config import settings
from ..models import GmailAccount, ProcessedEmail
from .gmail_client import extract_email_fields, fetch_latest_messages, send_email
from .whatsapp import send_whatsapp_summary


def process_latest_emails(db: Session, account: GmailAccount, batch_size: int = 10) -> dict[str, int]:
    raw_messages = fetch_latest_messages(account, max_results=batch_size)
    processed_count = 0
    relevant_count = 0

    for raw in raw_messages:
        fields = extract_email_fields(raw)
        if not fields['id']:
            continue

        exists = db.query(ProcessedEmail).filter(ProcessedEmail.gmail_message_id == fields['id']).first()
        if exists:
            continue

        state = {
            'subject': fields['subject'],
            'sender': fields['from'],
            'snippet': fields['snippet'],
            'is_relevant': False,
            'confidence_reason': '',
        }
        result = email_agent.invoke(state)

        processed = ProcessedEmail(
            user_id=account.user_id,
            gmail_message_id=fields['id'],
            subject=fields['subject'],
            sender=fields['from'],
            snippet=fields['snippet'],
            is_relevant=result['is_relevant'],
        )

        if result['is_relevant']:
            relevant_count += 1
            processed.forwarded_to = settings.FORWARD_TO_EMAIL
            forward_subject = f"FWD Lead Candidate: {fields['subject']}"
            forward_body = (
                f"Sender: {fields['from']}\n"
                f"Subject: {fields['subject']}\n"
                f"Snippet: {fields['snippet']}\n"
                f"Reason: {result['confidence_reason']}"
            )
            send_email(account, settings.FORWARD_TO_EMAIL, forward_subject, forward_body)

            sent_wa = send_whatsapp_summary(
                f"New lead-like email from {fields['from']} | Subject: {fields['subject']}"
            )
            processed.whatsapp_notified = sent_wa

        db.add(processed)
        processed_count += 1

    db.commit()
    return {
        'processed': processed_count,
        'relevant': relevant_count,
        'ignored': processed_count - relevant_count,
    }


def generate_reply_and_send(account: GmailAccount, to_email: str, original_context: str, intent: str) -> None:
    body = (
        'Hi,\n\n'
        'Thank you for reaching out.\n\n'
        f'Based on your message: "{original_context[:500]}"\n'
        f'Our intended response: {intent}.\n\n'
        'Can we schedule a short call to discuss next steps?\n\nBest regards'
    )
    send_email(account, to_email, 'Re: Follow-up', body)
