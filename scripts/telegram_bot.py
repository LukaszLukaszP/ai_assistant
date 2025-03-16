from telegram import Update, Bot
from telegram.ext import Application, MessageHandler, CallbackContext, filters
from scripts.llm import process_intent, chat_with_deepseek
from scripts.email_service import send_email
from scripts.calendar_service import add_calendar_event
from scripts.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
import asyncio

# Inicjalizacja bota
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
bot = Bot(token=TELEGRAM_BOT_TOKEN)

async def start(update: Update, context: CallbackContext):
    """Opcjonalne przywitanie, gdy użytkownik wyśle /start."""
    await update.message.reply_text("Cześć! Jestem Twoim asystentem AI. Możesz pisać do mnie w naturalnym języku!")

async def handle_message(update: Update, context: CallbackContext):
    # Ignoruj wiadomości, które sam bot wysłał
    if update.effective_user and update.effective_user.is_bot:
        return
    
    """Obsługuje wiadomości użytkownika i rozpoznaje intencję."""
    user_message = update.message.text
    intent_data = process_intent(user_message)

    if intent_data["type"] == "email":
        # Wywołaj funkcję wysyłania maila
        send_email(intent_data["recipient"], intent_data["subject"], intent_data["body"])
        await update.message.reply_text(f"📧 Wysłano e-mail do {intent_data['recipient']}!")
    
    elif intent_data["type"] == "event":
        # Wywołaj funkcję dodawania wydarzenia
        add_calendar_event(intent_data["summary"], intent_data["start_time"], intent_data["end_time"])
        await update.message.reply_text(f"📅 Dodano wydarzenie: {intent_data['summary']}!")
    
    else:
        # Dla naturalnej rozmowy wywołujemy LLM, aby wygenerował odpowiedź
        response_text = chat_with_deepseek(user_message)
        await update.message.reply_text(response_text)

# Rejestracja tylko handlera wiadomości tekstowych
application.add_handler(MessageHandler(filters.TEXT, handle_message))
# Opcjonalnie – pozostaw handler dla /start, jeśli chcesz przywitać użytkownika
application.add_handler(MessageHandler(filters.COMMAND, start))

def send_telegram_message(message: str):
    """Synchronous wrapper do wysłania wiadomości na Telegrama, używany przez API."""
    return asyncio.run(_send_telegram_message(message))

async def _send_telegram_message(message: str):
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    return "Notification sent"

# Uruchomienie bota
def run_telegram_bot():
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    run_telegram_bot()
