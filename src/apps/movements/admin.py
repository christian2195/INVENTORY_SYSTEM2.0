# src/apps/movements/admin.py
from django.contrib import admin
from .models import Movement  # Importa los modelos

# Crea una clase de Admin para personalizar la visualización en el panel
class MovementAdmin(admin.ModelAdmin):
    list_display = ('movement_type', 'product', 'quantity', 'date', 'created_by')
    list_filter = ('movement_type', 'date', 'product')
    search_fields = ('product__description', 'product__code')
    date_hierarchy = 'date'

class EntryAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'date')
    list_filter = ('date',)
    date_hierarchy = 'date'

# Registra los modelos con sus clases de Admin correspondientes
admin.site.register(Movement, MovementAdmin)
#admin.site.register(Entry, EntryAdmin)