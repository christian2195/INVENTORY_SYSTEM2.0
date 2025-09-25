from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Client, Supplier, Product, Warehouse
from .resources import ProductResource

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'phone', 'email')
    list_per_page = 20

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'phone', 'email', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'contact_person')
    list_per_page = 20
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_classes = [ProductResource]
    list_display = (
        'product_code',
        'description',
        'current_stock',
        'unit',
        'unit_price',
        'min_stock',
        'max_stock',
        'location',
        'category',
        'supplier',
        'warehouse',
        'is_active',
        'created_at',
    )
    list_filter = ('category', 'is_active', 'supplier', 'warehouse')
    search_fields = ('product_code', 'description')
    list_per_page = 20

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'location',) # Corregido: 'is_active' ha sido eliminado.
    list_filter = () # Corregido: 'is_active' ha sido eliminado.
    search_fields = ('name',)
    list_per_page = 20