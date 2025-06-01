FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ключевые изменения:
ENV PYTHONPATH=/app/backend
ENV DJANGO_SETTINGS_MODULE=backend.config.settings

# Для отладки (можно удалить после)
RUN echo "Содержимое /app/backend:" && ls -la /app/backend

CMD ["sh", "-c", "python bot/bot.py & gunicorn --bind 0.0.0.0:8000 backend.config.wsgi:application"]