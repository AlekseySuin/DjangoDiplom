from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.file_list, name='file_list'),
    path('upload/', views.upload_file, name='upload_file'),
    path('online/', views.online, name='online'),
    path('process_video/', views.process_video_view, name='process_video'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)