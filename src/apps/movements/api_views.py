# src/apps/movements/api_views.py
from rest_framework import viewsets
from .models import Movement
from .serializers import MovementSerializer

class MovementViewSet(viewsets.ModelViewSet):
    queryset = Movement.objects.all().order_by('-date')
    serializer_class = MovementSerializer