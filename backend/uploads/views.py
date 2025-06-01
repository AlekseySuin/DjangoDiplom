from summarizer.stt import transcribe_audio
from summarizer.llm import summarize_text
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from backend.uploads.forms import UploadFileForm
from backend.uploads.models import UploadedFile
import os

"""
web-1  | {"access_token":"eyJjdHkiOiJqd3QiLCJlbmMiOiJBMjU2Q0JDLUhTNTEyIiwiYWxnIjoiUlNBLU9BRVAtMjU2In0.txpA3J_IIATOXfXdYOHgQa-LF7igEiOUiBES_S-gcYrfaQPKTtq39cdPOC30z5JIO0QM7HxOTmCif-ESE696mARvfZSDN82m9OMnalth5fAiI4aAneCUmApLja1NlK
NI9K1v5RtDmfP8Z8KmJ_e0v8KHwWP0p1ql_qrKw0PbQS9TEWNsE6ZYrJJvpS8-yNU31dbA2Sg0YzjC2cRG95mNPtWBSD0f6nFUiymMUe6yxluUp7Box5AMF_9t0Kk4SvZ21PUKsTWJCJVzZDOzQcQFsEIX7iL4DuUEJpkzyF8Eu8s34YXhHVkM5aegz2yljYX0MO_nDuFGRawZOcIhxK4yZA.Mn0ot3WoWUN
LRAY2uOvFkg.zlOxTl_ceNvg4iD4j8gWeBR1xbjqE3et6-Xt3sHxdeyOMLpy1yQChPYo_ccbaTm4qjMy8bhr9Xw-NELRN019Qq-fix9SXBXfekzeurBmo2PqgUk3kigFCBeBD_LyVxdtcXev4wb3ioLKenARrCrigyE3OPV5kM7jM9AKjk_nKpv57DWTIcmgldj6opF489REvzMFDGdR0b8o1w79jYxTX6kd
0HeqPaCHdXfE97lYf3kVMseBdP-umyUiFk9ezT9ks5gF2jG-LGKoPwjNypcoeIfu4LHnQibmy2H1NJtaiB1LtVl8_MJMywtRa8u1Rwy3HcAw5-dhDNK240nEwAhhDMfALcw8XS2Q6IZaAAApf2Nx38eroZeovfoDys42tk2Wb_0mZAosqmPlS8NGNRYj_0jVZsvdJDfk9_5umG74y1awVDax9IsqH2MGnOBT
koBlg-46OWgEoMufYy_6LJlgCoez8dg9M5eE0Qz2zFi7rn3WbkR-DaR_xwFzZfF0yhGiXopPnm5di7tZkwDkZ1zKQGpCIhoceOoMu4zKWw-yoHTKVTRbTx-0heAuqDaTMuyqmogqyFUy_zpZZoHXwohKT-9SJmkeIPZyjGGTEc_xaWAXd6m3ySKvJTJL_kMur2nmI90k2KxVC1-hPmlUPlDveOK4071HydeZ
QRSS1eE4bGEzZJ9qbQNMVyappfkPte7rljQw83jDQX6ckypLbui-aZ7jKITec5YTvb8_y409TFA.0DU0KZpB1BIjVP6cIZP-_Ch2ZTUQ_YkVFivwXoEHYCU","expires_at":1748797655564}
web-1  | {"object":"list","data":[{"id":"GigaChat","object":"model","owned_by":"salutedevices","type":"chat"},{"id":"GigaChat-2","object":"model","owned_by":"salutedevices","type":"chat"},{"id":"GigaChat-2-Max","object":"model",
"owned_by":"salutedevices","type":"chat"},{"id":"GigaChat-2-Max-preview","object":"model","owned_by":"salutedevices","type":"chat"},{"id":"GigaChat-2-Pro","object":"model","owned_by":"salutedevices","type":"chat"},{"id":"GigaCha
t-2-Pro-preview","object":"model","owned_by":"salutedevices","type":"chat"},{"id":"GigaChat-2-preview","object":"model","owned_by":"salutedevices","type":"chat"},{"id":"GigaChat-Max","object":"model","owned_by":"salutedevices","
type":"chat"},{"id":"GigaChat-Max-preview","object":"model","owned_by":"salutedevices","type":"chat"},{"id":"GigaChat-Plus","object":"model","owned_by":"salutedevices","type":"chat"},{"id":"GigaChat-Plus-preview","object":"model
","owned_by":"salutedevices","type":"chat"},{"id":"GigaChat-Pro","object":"model","owned_by":"salutedevices","type":"chat"},{"id":"GigaChat-Pro-preview","object":"model","owned_by":"salutedevices","type":"chat"},{"id":"GigaChat-
preview","object":"model","owned_by":"salutedevices","type":"chat"},{"id":"Embeddings","object":"model","owned_by":"salutedevices","type":"embedder"},{"id":"Embeddings-2","object":"model","owned_by":"salutedevices","type":"embed
der"},{"id":"EmbeddingsGigaR","object":"model","owned_by":"salutedevices","type":"embedder"}]}
web-1  | job d8gukz4f1a submitted successfully, waiting for transcript
web-1  | Exception ignored in: <function _TemporaryFileCloser.__del__ at
"""
def upload_file(request):
    # Все файлы для отображения
    files = UploadedFile.objects.all().order_by('-uploaded_at')
    processing_files = files.filter(summary__isnull=False)
    completed_files = files.filter(summary__isnull=False)

    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                file = form.save()

                # Транскрибация и суммаризация
                transcript = transcribe_audio(file.file.path)
                summary = summarize_text(transcript)
                file.summary = summary
                file.save()

                return JsonResponse({
                    'status': 'success',
                    'summary': summary,
                    'file_id': file.id
                })
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                }, status=500)

    form = UploadFileForm()
    return render(request, 'uploads/index.html', {
        'form': form,
        'files': files,
        'processing_files': processing_files,
        'completed_files': completed_files
    })


@csrf_exempt
def delete_file(request, file_id):
    try:
        file = UploadedFile.objects.get(id=file_id)
        file_path = file.file.path
        if os.path.exists(file_path):
            os.remove(file_path)
        file.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)