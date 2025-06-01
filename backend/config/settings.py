import environ
from pathlib import Path
import os
import uuid

BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR.parent, '.env'))
env = environ.Env()
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')
DEBUG = True
ALLOWED_HOSTS = ['*']

# Telegram Bot
TELEGRAM_BOT_TOKEN = env('TELEGRAM_BOT_TOKEN')

# Speechmatics
SPEECHMATICS_API_KEY = "8eKbSukN5097FtrYF4fdQheDRkjE6uG9"

# GigaChat
AUTH_TOKEN = env('AUTH_TOKEN')
SECRET = env('SECRET')
GIGACHAT_SCOPE = env('GIGACHAT_SCOPE', default='GIGACHAT_API_PERS')
RQ_UID = str(uuid.uuid4())
VERIFY_SSL = env.bool('VERIFY_SSL', default=False)
CLIENT_ID = env('client_id')

# Prompt
PROMT = """
В вводе пользователя подаётся траскрипция какой-либо встречи. Необходимо определить вид встречи: собеседование или конференция.\n
Если эта встреча - собеседование: выдели основные темы разговора и ответы опрашиваемого.\n 
Если эта встреча - конференция: выдели основную цель конференции; выдели основные вопросы и выводы приведённые каждым участником конференции; 
выведи поставленные участникам конференции замечания при наличии таковых; 
выведи поставленные участникам конференции задачи при наличии таковых.\n 
Цели, вопросы, задачи и замечания должны различаться.\n
Если встреча не подходит под один из видов, то просто суммаризируй встречу.\n 
Пример: \nОсновные темы разговора и ответы опрашиваемого:\n
Личные данные: Полное имя (Ксения Выплакова), возраст (22 года) и семейное положение (не замужем). \n
Профессиональный опыт: Работа в колл-центре, предыдущий опыт работы в агентстве недвижимости.\n
Ожидания по зарплате: Минимальная зарплата — 25 000 рублей, максимальная — 32 500 рублей.\n
Причины ухода с предыдущей работы: Чувство дискомфорта в связи с возрастом коллектива.\n
Навыки и компетенции: Умение убеждать, оценка своих навыков на уровне 9 из 10.\n
Готовность к новой работе: Готовность приступить к обязанностям с понедельника после успешного выполнения тестового задания.\n
Пример совещания:\nВид встречи: конференция\n
Основная цель конференции: Обсуждение кредитно-денежной политики и приватизации финансовых учреждений, в частности Сбербанка.\n
Основные вопросы:\n1. Обсуждение кредитно-денежной политики в соответствии с законом о независимости Центрального банка.\n
2. Обсуждение планов приватизации, включая возможную приватизацию части пакета акций Сбербанка.\n
3. Сохранение контрольного пакета акций Сбербанка в руках государства, основываясь на доверии граждан и вкладчиков.\n
Выводы участников конференции:\n1. Центральный банк является самостоятельным финансовым учреждением с собственной компетенцией, и его независимость должна быть сохранена.\n
2. Приватизация части пакета акций Сбербанка на данный момент нецелесообразна, так как это может подорвать доверие граждан и вкладчиков.\n
3. Вопрос о приватизации части пакета акций Сбербанка не будет рассматриваться в ближайшее время.\nЗамечания участникам конференции:\n
1. Поддержание контроля государства над Сбербанком для сохранения доверия граждан и вкладчиков.\n
2. Исключение вопроса о приватизации части пакета акций Сбербанка из плана приватизации на 2016 год.
"""

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'backend.uploads',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # Добавьте эту строку
                'django.contrib.auth.context_processors.auth',  # Добавьте эту строку
                'django.contrib.messages.context_processors.messages',  # Добавьте эту строку
            ],
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/uploads/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Для сборки статики в production
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'uploads/static'),  # Путь к папке с исходными статическими файлами
]

MEDIA_ROOT = os.path.join(BASE_DIR.parent, 'media')
MEDIA_URL = '/media/'

LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler'
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO'
    },
}