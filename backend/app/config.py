from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    DATABASE_URL: str = 'postgresql+psycopg2://postgres:postgres@localhost:5432/lead_mailer'
    SECRET_KEY: str = 'change-me'
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    OPENAI_API_KEY: str = ''

    GOOGLE_CLIENT_ID: str = ''
    GOOGLE_CLIENT_SECRET: str = ''
    GOOGLE_REDIRECT_URI: str = 'http://localhost:8000/auth/gmail/callback'

    FORWARD_TO_EMAIL: str = 'sales-team@example.com'

    TWILIO_ACCOUNT_SID: str = ''
    TWILIO_AUTH_TOKEN: str = ''
    TWILIO_WHATSAPP_FROM: str = ''
    TWILIO_WHATSAPP_TO: str = ''


settings = Settings()
