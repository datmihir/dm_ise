# in api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_file, name='upload_file'),
    path('preview/<str:filename>/', views.preview_file, name='preview_file'),
    path('process/', views.process_data, name='process_data'),
    path('classify/', views.classify_data, name='classify_data'),
]