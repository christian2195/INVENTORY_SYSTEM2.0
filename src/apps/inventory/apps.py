# src/apps/inventory/apps.py
from django.apps import AppConfig

class InventoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.inventory'  # Full Python path to the app
    label = 'inventory'  # Optional: explicit label (must be unique)