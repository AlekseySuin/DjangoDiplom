from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import UploadedFile
from .forms import UploadFileForm
from django.conf import settings
from .stt_summarization import ourTranscribe

def upload_file(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save()

            text = ourTranscribe(file.file.path,'расскажи кратко о чем эта запись')
            file.summary = text
            file.save()
            return JsonResponse({'success':True})
    else:
        form = UploadFileForm()
    return render(request, 'files/upload.html', {'form':form})

def file_list(request):
    files = UploadedFile.objects.all()
    return render(request, 'files/list.html', {'files':files})
# Create your views here.
