# src/apps/reception_notes/admin.py
from django.contrib import admin
from .models import ReceptionNote, ReceptionItem

class ReceptionItemInline(admin.TabularInline):
    model = ReceptionItem
    extra = 1

@admin.register(ReceptionNote)
class ReceptionNoteAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'supplier', 'receipt_date', 'status')
    list_filter = ('receipt_date', 'status', 'supplier')
    search_fields = ('receipt_number', 'supplier__name', 'notes')
    inlines = [ReceptionItemInline]