import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..auth import (
    create_access_token,
    create_oauth_state_token,
    get_current_user,
    hash_password,
    validate_oauth_state_token,
    verify_password,
)
from ..database import get_db
from ..models import GmailAccount, User
from ..schemas import LoginRequest, RegisterRequest, TokenResponse
from ..services.gmail_client import GMAIL_SCOPES, build_gmail_flow

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/register', response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail='Email already registered')

    user = User(email=payload.email, hashed_password=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenResponse(access_token=create_access_token(user.email))


@router.post('/login', response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail='Invalid email or password')
    return TokenResponse(access_token=create_access_token(user.email))


@router.get('/gmail/connect')
def connect_gmail(current_user: User = Depends(get_current_user)):
    oauth_state = create_oauth_state_token(current_user.id, current_user.email)
    flow = build_gmail_flow(state=oauth_state)
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent',
    )
    return {'authorization_url': auth_url}


@router.get('/gmail/callback')
def gmail_callback(code: str = Query(...), state: str = Query(...), db: Session = Depends(get_db)):
    flow = build_gmail_flow(state=state)
    flow.fetch_token(code=code)
    creds = flow.credentials

    state_payload = validate_oauth_state_token(state)
    user = db.query(User).filter(User.id == int(state_payload['uid'])).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    if user.email != state_payload['sub']:
        raise HTTPException(status_code=401, detail='OAuth state/user mismatch')

    account = db.query(GmailAccount).filter(GmailAccount.user_id == user.id).first()
    if not account:
        account = GmailAccount(user_id=user.id, gmail_email=user.email, access_token='')
        db.add(account)

    account.access_token = creds.token
    account.refresh_token = creds.refresh_token
    account.token_uri = creds.token_uri
    account.client_id = creds.client_id
    account.client_secret = creds.client_secret
    account.scopes = ' '.join(creds.scopes or GMAIL_SCOPES)

    db.commit()
    return {'status': 'gmail connected'}


@router.get('/me')
def me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    account = db.query(GmailAccount).filter(GmailAccount.user_id == current_user.id).first()
    return {
        'email': current_user.email,
        'gmail_connected': bool(account),
        'gmail_scopes': json.loads(json.dumps((account.scopes if account else '').split(' '))),
    }
