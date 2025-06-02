FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH="${PYTHONPATH}:/app:/app/backend"
ENV DJANGO_SETTINGS_MODULE="backend.config.settings"

RUN echo "Проверка структуры:" && \
    ls -la && \
    ls -la backend && \
    ls -la backend/config

CMD ["sh", "-c", "rm -f /tmp/bot.lock && python bot/bot.py & gunicorn --bind 0.0.0.0:8000 backend.config.wsgi:application"]