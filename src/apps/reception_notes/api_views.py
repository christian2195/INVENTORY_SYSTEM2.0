# src/apps/reception_notes/api_views.py
from rest_framework import viewsets
from .serializers import ReceptionNoteSerializer, ReceptionItemSerializer
from .models import ReceptionNote, ReceptionItem

class ReceptionNoteViewSet(viewsets.ModelViewSet):
    queryset = ReceptionNote.objects.all().order_by('-receipt_number') # <--- CORRECCIÓN AQUÍ
    serializer_class = ReceptionNoteSerializer

class ReceptionItemViewSet(viewsets.ModelViewSet):
    queryset = ReceptionItem.objects.all()
    serializer_class = ReceptionItemSerializer