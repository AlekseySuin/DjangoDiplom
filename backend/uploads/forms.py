from django import forms
from backend.uploads.models import UploadedFile


class UploadFileForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['file', 'file_type']
        widgets = {
            'file_type': forms.Select(choices=[
                ('audio', 'Аудио'),
                ('video', 'Видео'),
                ('text', 'Текст')
            ])
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file_type'].required = True
        self.fields['file_type'].label = 'Тип файла'
        self.fields['file'].label = 'Файл'