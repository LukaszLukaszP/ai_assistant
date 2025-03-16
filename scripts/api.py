from fastapi import FastAPI
from scripts.email_service import send_email
from scripts.calendar_service import add_calendar_event
from scripts.telegram_bot import send_telegram_message

app = FastAPI()

@app.post("/send_email")
def email_handler(recipient: str, subject: str, body: str):
    return send_email(recipient, subject, body)

@app.post("/add_event")
def event_handler(summary: str, start_time: str, end_time: str):
    return add_calendar_event(summary, start_time, end_time)

@app.post("/send_telegram")
def telegram_handler(message: str):
    return send_telegram_message(message)
