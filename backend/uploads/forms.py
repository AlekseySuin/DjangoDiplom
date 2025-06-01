from django import forms
from backend.uploads.models import UploadedFile


class UploadFileForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['file', 'file_type']
        widgets = {
            'file': forms.FileInput(attrs={'accept': 'audio/*,video/*'}),
            'file_type': forms.Select(choices=UploadedFile.file_type)
        }