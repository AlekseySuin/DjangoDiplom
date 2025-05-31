import os
import sys
import logging
import uuid
from pathlib import Path
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь мне голосовое сообщение или аудиофайл, и я сделаю его суммаризацию.")

# Обработка аудио/голосовых сообщений
async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message

    if message.voice:
        file_id = message.voice.file_id
        file_name = f"{uuid.uuid4()}.ogg"
    elif message.audio:
        file_id = message.audio.file_id
        file_name = message.audio.file_name or f"{uuid.uuid4()}.mp3"
    else:
        return

    # Путь для сохранения
    media_dir = Path("media/uploads")
    media_dir.mkdir(parents=True, exist_ok=True)
    file_path = media_dir / file_name

    # Скачиваем файл
    file = await context.bot.get_file(file_id)
    await file.download_to_drive(file_path)

    # Транскрипция и суммаризация (через нашу функцию)
    try:
        from stt_summarization import ourTranscribe
        summary = ourTranscribe(str(file_path), "В вводе пользователя подаётся траскрипция какой-либо встречи. Необходимо определить вид встречи: собеседование или конференция.\nЕсли эта встреча - собеседование: выдели основные темы разговора и ответы опрашиваемого.\n Если эта встреча - конференция: выдели основную цель конференции; выдели основные вопросы и выводы приведённые каждым участником конференции; выведи поставленные участникам конференции замечания при наличии таковых; выведи поставленные участникам конференции задачи при наличии таковых.\n")
    except Exception as e:
        logger.error(f"Ошибка при обработке файла: {e}")
        await update.message.reply_text("Ошибка при обработке файла.")
        return

    # Сохраняем в БД (если модель UploadedFile определена)
    try:
        from files.models import UploadedFile
        uploaded_file = UploadedFile(
            file=file_path.relative_to("media"),
            summary=summary
        )
        uploaded_file.save()
    except Exception as e:
        logger.warning(f"Не удалось сохранить в БД: {e}")

    # Отправляем результат
    await update.message.reply_text("Суммаризация завершена:")
    await update.message.reply_text(summary)

    # Опционально: отправить как файл
    summary_file_path = media_dir / f"{uuid.uuid4()}_summary.txt"
    with open(summary_file_path, 'w', encoding='utf-8') as f:
        f.write(summary)
    await update.message.reply_document(document=open(summary_file_path, 'rb'))

# Функция запуска бота
def run_bot():
    from django.conf import settings
    app = ApplicationBuilder().token(settings.TG_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_audio))

    logger.info("Запуск Telegram-бота...")
    app.run_polling()