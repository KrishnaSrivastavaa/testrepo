from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models import GmailAccount, User
from ..schemas import TriggerResponse
from ..services.email_processor import generate_reply_and_send, process_latest_emails

router = APIRouter(prefix='/automation', tags=['automation'])


@router.post('/trigger', response_model=TriggerResponse)
def trigger_agent(batch_size: int = 10, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    account = db.query(GmailAccount).filter(GmailAccount.user_id == current_user.id).first()
    if not account:
        raise HTTPException(status_code=400, detail='Connect Gmail first')

    result = process_latest_emails(db=db, account=account, batch_size=min(max(batch_size, 1), 10))
    return TriggerResponse(**result)


@router.post('/reply')
def send_reply(
    to_email: str,
    original_context: str,
    intent: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = db.query(GmailAccount).filter(GmailAccount.user_id == current_user.id).first()
    if not account:
        raise HTTPException(status_code=400, detail='Connect Gmail first')

    generate_reply_and_send(account, to_email=to_email, original_context=original_context, intent=intent)
    return {'status': 'reply sent'}
