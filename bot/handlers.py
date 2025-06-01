from telegram.ext import ContextTypes
from telegram import Update
import logging
import uuid
import os
from asgiref.sync import sync_to_async
from django.core.files import File
from django.conf import settings

from summarizer.stt import transcribe_audio
from summarizer.llm import summarize_text
from backend.uploads.models import UploadedFile

# Отключаем предупреждения SSL (только для разработки!)
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь мне голосовое сообщение или аудиофайл.")

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not (message.voice or message.audio):
        return

    try:
        # Скачиваем файл
        file_id = message.voice.file_id if message.voice else message.audio.file_id
        original_name = message.audio.file_name if message.audio else "voice_message.ogg"
        file_ext = os.path.splitext(original_name)[1] if message.audio else ".ogg"
        file_name = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(settings.MEDIA_ROOT, "uploads", file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        file = await context.bot.get_file(file_id)
        await file.download_to_drive(file_path)

        # Обработка в синхронном контексте
        transcript = await sync_to_async(transcribe_audio)(file_path)
        summary = await sync_to_async(summarize_text)(transcript)

        # Сохранение в БД через sync_to_async
        with open(file_path, 'rb') as f:
            django_file = File(f, name=file_name)
            uploaded_file = await sync_to_async(UploadedFile.objects.create)(
                file=django_file,
                file_type='audio',
                summary=summary,
                original_name=original_name,
                user_id=str(update.effective_user.id),
                chat_id=str(update.effective_chat.id)
            )

        # Ответ пользователю
        await update.message.reply_text("✅ Суммаризация завершена:")
        await update.message.reply_text(summary)

    except Exception as e:
        logger.error(f"Ошибка обработки файла: {e}", exc_info=True)
        await update.message.reply_text("Произошла ошибка при обработке файла. Попробуйте позже.")