from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import os
from scripts.llm import process_intent
from scripts.email_service import send_email
from scripts.calendar_service import add_calendar_event
from scripts.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

# Inicjalizacja bota
bot = Bot(token=TELEGRAM_BOT_TOKEN)
updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Cześć! Jestem Twoim asystentem AI. Możesz pisać do mnie w naturalnym języku!")

def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text
    intent_data = process_intent(user_message)

    if intent_data["type"] == "email":
        send_email(intent_data["recipient"], intent_data["subject"], intent_data["body"])
        update.message.reply_text(f"📧 Wysłano e-mail do {intent_data['recipient']}!")
    
    elif intent_data["type"] == "event":
        event_id = add_calendar_event(intent_data["summary"], intent_data["start_time"], intent_data["end_time"])
        update.message.reply_text(f"📅 Dodano wydarzenie: {intent_data['summary']}!")

    else:
        update.message.reply_text(intent_data["message"])

# Dodanie obsługi komend
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# Uruchomienie bota
def run_telegram_bot():
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    run_telegram_bot()