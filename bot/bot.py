import os
import sys
import django
import fcntl
from pathlib import Path
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# Настройка Django
sys.path.extend(['/app', '/app/backend'])
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.config.settings")
django.setup()

from django.conf import settings
from handlers import handle_audio, start


def acquire_lock():
    """Блокировка для предотвращения запуска нескольких экземпляров"""
    lock_file = '/tmp/bot.lock'
    fd = os.open(lock_file, os.O_CREAT | os.O_RDWR)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return fd
    except BlockingIOError:
        print("⚠️ Другой экземпляр бота уже запущен!")
        os.close(fd)
        exit(1)


def run_bot():
    """Запуск бота с защитой от конфликтов"""
    application = ApplicationBuilder() \
        .token(settings.TELEGRAM_BOT_TOKEN) \
        .build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_audio))

    print("🤖 Бот запущен. Ожидание сообщений...")

    # Критически важные параметры polling:
    application.run_polling(
        drop_pending_updates=True,  # Игнорировать старые сообщения при старте
        close_loop=False,  # Не закрывать event loop при ошибке
        stop_signals=None,  # Обрабатывать сигналы завершения
        poll_interval=1.0,  # Интервал опроса сервера
        timeout=30,  # Таймаут соединения
        allowed_updates=None  # Получать все типы обновлений
    )


if __name__ == "__main__":
    lock_fd = acquire_lock()
    try:
        run_bot()
    except Exception as e:
        print(f"🚨 Ошибка в основном цикле: {str(e)}")
    finally:
        # Освобождение блокировки при завершении
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        os.close(lock_fd)
        try:
            os.remove('/tmp/bot.lock')
        except:
            pass