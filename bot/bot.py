import os
import sys
import django
import fcntl
from pathlib import Path

# Настройка Django
sys.path.extend(['/app', '/app/backend'])
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.config.settings")
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
    application.run_polling(
        drop_pending_updates=True,
        close_loop=False,
        stop_signals=None,
        allowed_updates=None
    )

def check_single_instance():
    lock_file = '/tmp/bot.lock'
    fd = os.open(lock_file, os.O_CREAT | os.O_RDWR)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return fd
    except BlockingIOError:
        print("❌ Другой экземпляр бота уже запущен!")
        os.close(fd)
        exit(1)

if __name__ == "__main__":
    lock_fd = check_single_instance()
    try:
        run_bot()
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        os.close(lock_fd)
        try:
            os.unlink('/tmp/bot.lock')
        except:
            pass
