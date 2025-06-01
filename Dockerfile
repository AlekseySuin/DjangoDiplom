# Базовый образ
FROM python:3.10-slim


# Рабочая директория
WORKDIR /app

# Копирование зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

ENV PYTHONPATH=/app/backend
ENV DJANGO_SETTINGS_MODULE=config.settings

# Команда для запуска
CMD ["sh", "-c", "python bot/bot.py & gunicorn --bind 0.0.0.0:8000 backend.wsgi"]