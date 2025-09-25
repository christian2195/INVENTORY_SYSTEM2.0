# apps/inventory/management/commands/populate_products.py
from django.core.management.base import BaseCommand
from apps.inventory.models import Product, Supplier, Warehouse

class Command(BaseCommand):
    help = 'Populate database with sample products'

    def handle(self, *args, **options):
        # ... el mismo código de arriba ...
        self.stdout.write(self.style.SUCCESS('Productos de prueba creados exitosamente!'))