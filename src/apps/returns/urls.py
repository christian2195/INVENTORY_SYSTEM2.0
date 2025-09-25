# src/apps/returns/urls.py
from django.urls import path
from . import views

app_name = 'returns'

urlpatterns = [
    path('', views.ReturnNoteListView.as_view(), name='list'),
    path('nuevo/', views.ReturnNoteCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ReturnNoteDetailView.as_view(), name='detail'),
    path('procesar/<int:pk>/', views.process_return_note, name='process'),
]