import os
import tempfile
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import UploadedFile
from .forms import UploadFileForm
from .face_transcribe import process_video
from .stt_summarization import ourTranscribe
import subprocess
import logging

@csrf_exempt
def upload_file(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save()

            text = ourTranscribe(file.file.path, "В вводе пользователя подаётся траскрипция какой-либо встречи. Необходимо определить вид встречи: собеседование или конференция.\nЕсли эта встреча - собеседование: выдели основные темы разговора и ответы опрашиваемого.\n Если эта встреча - конференция: выдели основную цель конференции; выдели основные вопросы и выводы приведённые каждым участником конференции; выведи поставленные участникам конференции замечания при наличии таковых; выведи поставленные участникам конференции задачи при наличии таковых.\n")
            file.summary = text
            file.save()
            return JsonResponse({'success':True})
    else:
        form = UploadFileForm()
    return render(request, 'files/upload.html', {'form':form})

def file_list(request):
    files = UploadedFile.objects.all()
    return render(request, 'files/list.html', {'files':files})

def online(request):
    return render(request, 'files/online.html')


ALLOWED_EXTENSIONS = {'webm', 'mp4'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



logger = logging.getLogger(__name__)

@csrf_exempt
def api_summarize(request):
    if request.method == 'POST' and request.FILES.get('audio'):
        audio_file = request.FILES['audio']
        summary = summarize_audio(audio_file)  # Ваш код обработки
        return JsonResponse({"summary": summary})
    return JsonResponse({"error": "Invalid request"}, status=400)
@csrf_exempt
def process_video_view(request):
    # Минимальная версия без конвертации и обработки
    try:
        # Проверяем наличие файла
        if 'video' not in request.FILES:
            return JsonResponse({'error': 'No video file'}, status=400)

        # Просто получаем файл и возвращаем тестовый ответ
        video_file = request.FILES['video']
        file_size = video_file.size

        logger.info(f"Received video file: {video_file.name}, size: {file_size} bytes")

        # Шаг 2: Сохранение файла
        input_path = os.path.join(settings.MEDIA_ROOT, f'video/{video_file}')
        with open(input_path, 'wb+') as f:
            for chunk in video_file.chunks():
                f.write(chunk)
        logger.info(f"File saved to {input_path}")

        output_name = video_file.name.split('.', maxsplit=1)[0]
        output_path = os.path.join(settings.MEDIA_ROOT, f"video/{output_name}.mp4")
        os.system(f'ffmpeg -i "{input_path}" -c copy "{output_path}"')

        # Временный тестовый ответ
        return JsonResponse({
            'status': 'success',
            'message': f'Received {file_size} bytes',
            'transcription': [{
                'name': 'Test Speaker',
                'start': 0.0,
                'end': 1.0,
                'text': 'This is a test transcription'
            }]
        })

    except Exception as e:
        logger.error("Video processing failed", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'type': type(e).__name__
        }, status=500)


# def process_video_view(request):
#     if request.method != 'POST':
#         return JsonResponse({'error': 'Only POST allowed'}, status=405)
#
#     if 'video' not in request.FILES:
#         return JsonResponse({'error': 'No video file'}, status=400)
#
#     try:
#         # Сохраняем временный файл
#         with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as tmp:
#             for chunk in request.FILES['video'].chunks():
#                 tmp.write(chunk)
#             temp_path = tmp.name
#
#         # Конвертируем в MP4 если нужно
#         if temp_path.endswith('.webm'):
#             mp4_path = temp_path.replace('.webm', '.mp4')
#             subprocess.run([
#                 'ffmpeg', '-i', temp_path,
#                 '-c:v', 'libx264', '-preset', 'fast',
#                 '-c:a', 'aac', mp4_path
#             ], check=True)
#             os.unlink(temp_path)
#             temp_path = mp4_path
#
#         # Обрабатываем видео
#         transcription = process_video(temp_path)
#
#         if not isinstance(transcription, list):
#             raise ValueError("Transcription result is not a list")
#
#         return JsonResponse({
#             'status': 'success',
#             'transcription': [
#                 {
#                     'name': str(name) if name else 'Unknown',
#                     'start': float(start) if start else 0.0,
#                     'end': float(end) if end else 0.0,
#                     'text': str(text) if text else ''
#                 }
#                 for name, start, end, text in transcription
#             ]
#         })
#
#     except subprocess.CalledProcessError as e:
#         return JsonResponse({'error': f'FFmpeg error: {e.stderr}'}, status=500)
#     except Exception as e:
#         return JsonResponse({
#             'status': 'error',
#             'error': str(e),
#             'transcription': []  # Гарантируем что transcription будет массивом
#         }, status=500)
#     finally:
#         # Удаляем временные файлы
#         if 'temp_path' in locals() and os.path.exists(temp_path):
#             os.unlink(temp_path)
#         if 'mp4_path' in locals() and os.path.exists(mp4_path):
#             os.unlink(mp4_path)


        # form = UploadFileForm(request.POST, request.FILES)
        # if form.is_valid():
        #     file = form.save()
        #
        #     text = ourTranscribe(wav_path, "В вводе пользователя подаётся траскрипция какой-либо встречи. Необходимо определить вид встречи: собеседование или конференция.\nЕсли эта встреча - собеседование: выдели основные темы разговора и ответы опрашиваемого.\n Если эта встреча - конференция: выдели основную цель конференции; выдели основные вопросы и выводы приведённые каждым участником конференции; выведи поставленные участникам конференции замечания при наличии таковых; выведи поставленные участникам конференции задачи при наличии таковых.\n")
        #     file.summary = text
        #     file.save()

