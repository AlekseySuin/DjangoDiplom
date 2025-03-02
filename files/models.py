from django.db import models

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_type = models.CharField(max_length=10, choices=[('text', 'Text'), ('audio', 'Audio'), ('video', 'Video')])
    summary = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.file.name} ({self.file_type})"