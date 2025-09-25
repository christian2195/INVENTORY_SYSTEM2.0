# check_models.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_system.settings')
django.setup()

from apps.inventory.models import Client, Supplier, Product, Warehouse

def check_model_fields():
    print("=== CAMPOS DE CLIENT ===")
    for field in Client._meta.fields:
        print(f"  - {field.name}")
    
    print("\n=== CAMPOS DE SUPPLIER ===")
    for field in Supplier._meta.fields:
        print(f"  - {field.name}")
    
    print("\n=== CAMPOS DE PRODUCT ===")
    for field in Product._meta.fields:
        print(f"  - {field.name}")
    
    print("\n=== CAMPOS DE WAREHOUSE ===")
    for field in Warehouse._meta.fields:
        print(f"  - {field.name}")

if __name__ == "__main__":
    check_model_fields()