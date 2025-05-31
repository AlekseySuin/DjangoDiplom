import os
import sys
from pathlib import Path

# Укажи корень проекта (папка, где находится manage.py)
project_dir = Path(__file__).resolve().parent
sys.path.append(str(project_dir))

# Установи настройки Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stt_summarization.settings")

# Запусти Django
import django
django.setup()

# Теперь можно импортировать bot
from files.bot import run_bot

if __name__ == "__main__":
    run_bot()