# src/apps/reception_notes/urls.py
from django.urls import path
from . import views

app_name = 'reception_notes'

urlpatterns = [
    path('', views.ReceptionNoteListView.as_view(), name='list'),
    path('nuevo/', views.ReceptionNoteCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ReceptionNoteDetailView.as_view(), name='detail'),
    path('editar/<int:pk>/', views.ReceptionNoteUpdateView.as_view(), name='update'),
    path('validar/<int:pk>/', views.validate_reception_note, name='validate'), # <-- AÑADIR ESTA LÍNEA
]