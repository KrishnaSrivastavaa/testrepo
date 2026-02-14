import requests

from ..config import settings


def send_whatsapp_summary(message: str) -> bool:
    if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_WHATSAPP_FROM, settings.TWILIO_WHATSAPP_TO]):
        return False

    url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json"
    payload = {
        'From': settings.TWILIO_WHATSAPP_FROM,
        'To': settings.TWILIO_WHATSAPP_TO,
        'Body': message,
    }
    response = requests.post(url, data=payload, auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN), timeout=20)
    return response.ok
