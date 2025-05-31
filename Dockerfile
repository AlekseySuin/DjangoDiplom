# Базовый образ
FROM python:3.10-slim

# Рабочая директория
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Команда для запуска обоих процессов
CMD ["sh", "-c", "cd stt_summarization && gunicorn stt_summarization.wsgi --bind 0.0.0.0:5000 & python runbot.py"]