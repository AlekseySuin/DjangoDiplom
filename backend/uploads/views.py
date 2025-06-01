import os
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from .forms import UploadFileForm
from backend.uploads.models import UploadedFile
from summarizer.stt import transcribe_audio
from summarizer.llm import summarize_text


def show_main(request):
    form = UploadFileForm()
    return render(request, 'uploads/index.html', {'form': form})

"""
@csrf_exempt
def upload_file(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save()
            transcript = transcribe_audio(file.file.path)
            summary = summarize_text(transcript)
            file.summary = summary
            file.save()
            return JsonResponse({'summary': summary})
    else:
        form = UploadFileForm()

    return render(request, 'uploads/index.html', {'form': form})
"""

def upload_file(request):
    processing_files = UploadedFile.objects.filter(summary__isnull=True)
    completed_files = UploadedFile.objects.filter(summary__isnull=False)

    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save(commit=False)
            file.user = request.user
            file.save()

            try:
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

        return JsonResponse({
            'status': 'error',
            'errors': form.errors.as_json()
        }, status=400)

    form = UploadFileForm()
    return render(request, 'uploads/index.html', {
        'form': form,
        'processing_files': processing_files,
        'completed_files': completed_files
    })


@csrf_exempt
def delete_file(request, file_id):
    file = get_object_or_404(UploadedFile, id=file_id, user=request.user)
    file.delete()
    return JsonResponse({'status': 'success'})