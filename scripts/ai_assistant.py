from telegram import Bot, Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
from scripts.config import TELEGRAM_BOT_TOKEN
from scripts.email_service import send_email
from scripts.calendar_service import add_calendar_event
from scripts.llm import chat_with_deepseek, analyze_intent

# Inicjalizacja bota
bot = Bot(token=TELEGRAM_BOT_TOKEN)
updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
dp = updater.dispatcher

# Obsługa każdej wiadomości użytkownika
def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text

    # Analiza intencji użytkownika
    intent = analyze_intent(user_message)

    if "email" in intent:
        update.message.reply_text("OK, piszę e-mail. Do kogo mam go wysłać?")
        context.user_data["action"] = "email"
    elif "event" in intent:
        update.message.reply_text("OK, dodaję wydarzenie do kalendarza. Podaj szczegóły.")
        context.user_data["action"] = "event"
    else:
        response = chat_with_deepseek(user_message)
        update.message.reply_text(response)

# Obsługa podawania danych do e-maila
def email_data(update: Update, context: CallbackContext):
    if context.user_data.get("action") == "email":
        update.message.reply_text("OK, wysyłam ten e-mail.")
        send_email("test@example.com", "Automatyczny temat", update.message.text)
        context.user_data["action"] = None
    else:
        handle_message(update, context)

# Obsługa podawania danych do wydarzenia
def event_data(update: Update, context: CallbackContext):
    if context.user_data.get("action") == "event":
        update.message.reply_text("OK, dodaję wydarzenie.")
        add_calendar_event("Nowe wydarzenie", "2024-03-11T10:00:00", "2024-03-11T11:00:00")
        context.user_data["action"] = None
    else:
        handle_message(update, context)

# Dodawanie handlerów do bota
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
dp.add_handler(MessageHandler(Filters.text & Filters.command, email_data))
dp.add_handler(MessageHandler(Filters.text & Filters.command, event_data))

# Uruchomienie bota
if __name__ == "__main__":
    updater.start_polling()
    updater.idle()