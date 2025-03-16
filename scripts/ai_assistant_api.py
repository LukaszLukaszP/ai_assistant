from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import os
from scripts.email_service import send_email
from scripts.calendar_service import add_calendar_event
from scripts.config import TELEGRAM_BOT_TOKEN
from scripts.llm import chat_with_deepseek

# Inicjalizacja bota
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# 🔹 Komenda /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Cześć! Jestem Twoim asystentem AI. Dostępne komendy:\n"
        "/email recipient subject body\n"
        "/event title start_time end_time\n"
        "/ask_deepseek [pytanie]"
    )

# 🔹 Obsługa komendy /email
async def email_command(update: Update, context: CallbackContext):
    try:
        args = context.args
        if len(args) < 3:
            await update.message.reply_text("Użyj: /email recipient subject body")
            return
        recipient, subject, body = args[0], args[1], " ".join(args[2:])
        result = send_email(recipient, subject, body)
        await update.message.reply_text(result)
    except Exception as e:
        await update.message.reply_text(f"Błąd: {e}")

# 🔹 Obsługa komendy /event
async def event_command(update: Update, context: CallbackContext):
    try:
        args = context.args
        if len(args) < 3:
            await update.message.reply_text("Użyj: /event title start_time end_time")
            return
        title, start_time, end_time = args[0], args[1], args[2]
        result = add_calendar_event(title, start_time, end_time)
        await update.message.reply_text(result)
    except Exception as e:
        await update.message.reply_text(f"Błąd: {e}")

# 🔹 Obsługa komendy /ask_deepseek
async def ask_deepseek_command(update: Update, context: CallbackContext):
    user_input = " ".join(context.args)
    if not user_input:
        await update.message.reply_text("Użyj: /ask_deepseek [Twoje pytanie]")
        return
    response = chat_with_deepseek(user_input)
    await update.message.reply_text(response)

# 🔹 Obsługa nieznanych komend
async def unknown(update: Update, context: CallbackContext):
    await update.message.reply_text("Nieznana komenda. Użyj /help")

# 🔹 Rejestracja komend
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("email", email_command))
application.add_handler(CommandHandler("event", event_command))
application.add_handler(CommandHandler("ask_deepseek", ask_deepseek_command))
application.add_handler(MessageHandler(filters.COMMAND, unknown))

# 🔹 Uruchomienie bota
def run_telegram_bot():
    application.run_polling()

if __name__ == "__main__":
    run_telegram_bot()