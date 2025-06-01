import os
import sys
from pathlib import Path

# Настройка Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
import django
django.setup()

# Теперь можно импортировать всё из Django
from django.conf import settings
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from handlers import handle_audio, start


def run_bot():
    application = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_audio))
    print("🤖 Telegram-бот запущен...")
    application.run_polling()


if __name__ == "__main__":
    run_bot()