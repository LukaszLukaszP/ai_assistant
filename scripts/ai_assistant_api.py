from fastapi import FastAPI, HTTPException
from googleapiclient.discovery import build
from google.oauth2 import service_account
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import os
from dotenv import load_dotenv
from openai import OpenAI

# Załaduj zmienne środowiskowe z pliku .env
load_dotenv("config/.env")

# Pobranie zmiennych
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
CALENDAR_ID = os.getenv("CALENDAR_ID")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

app = FastAPI()

# Inicjalizacja klienta OpenAI dla DeepSeek
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

def chat_with_deepseek(prompt: str):
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            stream=False  # Jeśli chcesz streamować odpowiedzi, zmień na True
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Błąd: {str(e)}"

# Funkcja do wysyłania e-maili
def send_email(recipient: str, subject: str, body: str):
    try:
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASS)
        server.sendmail(GMAIL_USER, recipient, msg.as_string())
        server.quit()
        return "Email sent successfully"
    except Exception as e:
        return str(e)

@app.post("/send_email")
def email_handler(recipient: str, subject: str, body: str):
    return send_email(recipient, subject, body)

# Konfiguracja Google Calendar API
SCOPES = ["https://www.googleapis.com/auth/calendar"]

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
calendar_service = build("calendar", "v3", credentials=credentials)

def add_calendar_event(summary: str, start_time: str, end_time: str):
    event = {
        "summary": summary,
        "start": {"dateTime": start_time, "timeZone": "UTC"},
        "end": {"dateTime": end_time, "timeZone": "UTC"},
    }
    event_result = calendar_service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    return "Event added: " + event_result["id"]

@app.post("/add_event")
def event_handler(summary: str, start_time: str, end_time: str):
    return add_calendar_event(summary, start_time, end_time)

# Konfiguracja Telegram Bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)

def send_telegram_message(message: str):
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    return "Notification sent"

@app.post("/send_telegram")
def telegram_handler(message: str):
    return send_telegram_message(message)

# Obsługa wiadomości w Telegramie
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Cześć! Jestem Twoim asystentem AI. Dostępne komendy: \n"
        "/email recipient subject body\n"
        "/event title start_time end_time\n"
        "/ask_deepseek [pytanie]"
    )

def email_command(update: Update, context: CallbackContext):
    try:
        args = context.args
        if len(args) < 3:
            update.message.reply_text("Użyj: /email recipient subject body")
            return
        recipient, subject, body = args[0], args[1], " ".join(args[2:])
        result = send_email(recipient, subject, body)
        update.message.reply_text(result)
    except Exception as e:
        update.message.reply_text(f"Błąd: {e}")

def event_command(update: Update, context: CallbackContext):
    try:
        args = context.args
        if len(args) < 3:
            update.message.reply_text("Użyj: /event title start_time end_time")
            return
        title, start_time, end_time = args[0], args[1], args[2]
        result = add_calendar_event(title, start_time, end_time)
        update.message.reply_text(result)
    except Exception as e:
        update.message.reply_text(f"Błąd: {e}")

def ask_deepseek_command(update: Update, context: CallbackContext):
    user_input = " ".join(context.args)
    if not user_input:
        update.message.reply_text("Użyj: /ask_deepseek [Twoje pytanie]")
        return
    response = chat_with_deepseek(user_input)
    update.message.reply_text(response)

def unknown(update: Update, context: CallbackContext):
    update.message.reply_text("Nieznana komenda. Użyj /help")

updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("email", email_command))
dp.add_handler(CommandHandler("event", event_command))
dp.add_handler(CommandHandler("ask_deepseek", ask_deepseek_command))
dp.add_handler(MessageHandler(Filters.command, unknown))

if __name__ == "__main__":
    updater.start_polling()
    updater.idle()