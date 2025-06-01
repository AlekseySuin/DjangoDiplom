# Базовый образ
FROM python:3.10-slim

# Рабочая директория
WORKDIR /app

# Копирование зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Установка переменных окружения
ENV PYTHONPATH=/app
ENV DJANGO_SETTINGS_MODULE=config.settings

# Проверка структуры (можно удалить после отладки)
RUN echo "Проверка структуры проекта:" && \
    ls -la /app && \
    ls -la /app/backend && \
    ls -la /app/bot

# Команда для запуска
CMD ["sh", "-c", "python bot/bot.py & gunicorn --bind 0.0.0.0:8000 config.wsgi:application"]