from django.db import models
import os
from django.conf import settings


class UploadedFile(models.Model):
    file = models.FileField(
        upload_to='uploads/',
        verbose_name='Файл'
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата загрузки'
    )
    file_type = models.CharField(
        max_length=10,
        choices=[
            ('text', 'Текст'),
            ('audio', 'Аудио'),
            ('video', 'Видео')
        ],
        verbose_name='Тип файла'
    )
    summary = models.TextField(
        blank=True,
        null=True,
        verbose_name='Суммаризация'
    )
    original_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Оригинальное имя файла'
    )
    user_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='ID пользователя'
    )
    chat_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='ID чата'
    )

    class Meta:
        app_label = 'uploads'
        verbose_name = 'Загруженный файл'
        verbose_name_plural = 'Загруженные файлы'

    def __str__(self):
        return f"{self.original_name or os.path.basename(self.file.name)} ({self.file_type})"

    def save(self, *args, **kwargs):
        # Автоматическое определение типа файла при сохранении
        if not self.file_type:
            ext = os.path.splitext(self.file.name)[1].lower()
            if ext in ['.txt', '.doc', '.docx', '.pdf']:
                self.file_type = 'text'
            elif ext in ['.mp3', '.wav', '.ogg', '.m4a']:
                self.file_type = 'audio'
            elif ext in ['.mp4', '.avi', '.mov']:
                self.file_type = 'video'

        super().save(*args, **kwargs)

    @classmethod
    def create_from_bot(cls, file_path, file_type=None, summary=None, original_name=None, user_id=None, chat_id=None):
        """Специальный метод для создания из бота"""
        # Генерируем относительный путь для Django
        rel_path = os.path.relpath(file_path, settings.MEDIA_ROOT)

        return cls.objects.create(
            file=rel_path,
            file_type=file_type,
            summary=summary,
            original_name=original_name,
            user_id=user_id,
            chat_id=chat_id
        )