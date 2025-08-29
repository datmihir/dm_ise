# in api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_file, name='upload_file'),
    path('preview/<str:filename>/', views.preview_file, name='preview_file'),
    path('process/', views.process_data, name='process_data'),
    path('classify/', views.classify_data, name='classify_data'),
    path('datasets/', views.list_datasets, name='list_datasets'),
    path('datasets/<int:dataset_id>/analyses/', views.list_dataset_analyses, name='list_dataset_analyses'),
]