# src/apps/reception_notes/serializers.py
from rest_framework import serializers
from .models import ReceptionNote, ReceptionItem

class ReceptionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceptionItem
        fields = '__all__'

class ReceptionNoteSerializer(serializers.ModelSerializer):
    items = ReceptionItemSerializer(many=True, read_only=True)

    class Meta:
        model = ReceptionNote
        fields = '__all__'