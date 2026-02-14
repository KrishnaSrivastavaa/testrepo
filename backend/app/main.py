from fastapi import FastAPI

from .database import Base, engine
from .routers import auth, automation

app = FastAPI(title='Lead Email Automation API')


@app.on_event('startup')
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get('/health')
def health():
    return {'status': 'ok'}


app.include_router(auth.router)
app.include_router(automation.router)
