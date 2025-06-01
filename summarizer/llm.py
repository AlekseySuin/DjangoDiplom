import requests
import json
from django.conf import settings
import uuid
import ffmpeg
import base64

client_id = settings.CLIENT_ID

secret = settings.SECRET

auth = settings.AUTH_TOKEN

promt = settings.PROMT
def get_token(auth_token, scope='GIGACHAT_API_PERS'):
    rq_uid = str(uuid.uuid4())

    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': rq_uid,
        'Authorization': f'Basic {auth_token}'
    }

    payload = {
        'scope': scope
    }

    try:
        response = requests.post(url, headers=headers, data=payload, verify=False)
        return response
    except requests.RequestException as e:
        print(f"Ошибка: {str(e)}")
        return -1

response = get_token(auth)
if response != 1:
  print(response.text)
  giga_token = response.json()['access_token']


url = "https://gigachat.devices.sberbank.ru/api/v1/models"

payload={}
headers = {
  'Accept': 'application/json',
  'Authorization': f'Bearer {giga_token}'
}

response = requests.request("GET", url, headers=headers, data=payload, verify=False)

print(response.text)


def convert_mp4_to_wav(input_path, output_path):
    try:
        ffmpeg.input(input_path).output(output_path, acodec='pcm_s16le').run()
        return output_path
    except ffmpeg.Error as e:
        print(f"Ошибка при преобразовании файла: {e.stderr}")
        raise

def get_chat_completion(auth_token, user_message):
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

    payload = json.dumps({
        "model": "GigaChat",  # Используемая модель
        "messages": [
            {
                "role": "system",  # Роль отправителя (пользователь)
                "content": "В вводе пользователя подаётся траскрипция какой-либо встречи. Необходимо определить вид встречи: собеседование или конференция.\nЕсли эта встреча - собеседование: выдели основные темы разговора и ответы опрашиваемого.\n Если эта встреча - конференция: выдели основную цель конференции; выдели основные вопросы и выводы приведённые каждым участником конференции; выведи поставленные участникам конференции замечания при наличии таковых; выведи поставленные участникам конференции задачи при наличии таковых.\n Пример: \nОсновные темы разговора и ответы опрашиваемого:\nЛичные данные: Полное имя (Ксения Выплакова), возраст (22 года) и семейное положение (не замужем). \nПрофессиональный опыт: Работа в колл-центре, предыдущий опыт работы в агентстве недвижимости.\nОжидания по зарплате: Минимальная зарплата — 25 000 рублей, максимальная — 32 500 рублей.\nПричины ухода с предыдущей работы: Чувство дискомфорта в связи с возрастом коллектива.\nНавыки и компетенции: Умение убеждать, оценка своих навыков на уровне 9 из 10.\nГотовность к новой работе: Готовность приступить к обязанностям с понедельника после успешного выполнения тестового задания."  # Содержание сообщения
            },
            {
                "role": "user",  # Роль отправителя (пользователь)
                "content": user_message  # Содержание сообщения
            }
        ],
        "temperature": 1,  # Температура генерации
        "top_p": 0.1,  # Параметр top_p для контроля разнообразия ответов
        "n": 1,  # Количество возвращаемых ответов
        "stream": False,  # Потоковая ли передача ответов
        "max_tokens": 512,  # Максимальное количество токенов в ответе
        "repetition_penalty": 1,  # Штраф за повторения
        "update_interval": 0  # Интервал обновления (для потоковой передачи)
    })

    # Заголовки запроса
    headers = {
        'Content-Type': 'application/json',  # Тип содержимого - JSON
        'Accept': 'application/json',  # Принимаем ответ в формате JSON
        'Authorization': f'Bearer {auth_token}'  # Токен авторизации
    }

    # Выполнение POST-запроса и возвращение ответа
    try:
        response = requests.request("POST", url, headers=headers, data=payload, verify=False)
        return response
    except requests.RequestException as e:
        # Обработка исключения в случае ошибки запроса
        print(f"Произошла ошибка: {str(e)}")
        return -1

def summarize_text(text):
    """Суммаризация через GigaChat"""
    credentials = f"{client_id}:{secret}"
    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

    encoded_credentials == auth
    answer = get_chat_completion(giga_token, promt + text)

    answer.json()
    print(answer.json()['choices'][0]['message']['content'])
    result = answer.json()['choices'][0]['message']['content']
    return result