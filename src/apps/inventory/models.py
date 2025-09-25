# src/apps/inventory/models.py
from django.db import models
from django.utils import timezone

class Client(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Supplier(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre")
    contact_person = models.CharField(max_length=100, blank=True, verbose_name="Persona de Contacto")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    email = models.EmailField(blank=True, verbose_name="Correo Electrónico")
    address = models.TextField(blank=True, verbose_name="Dirección")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['name']

    def __str__(self):
        return self.name

class Warehouse(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200, blank=True)
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Product(models.Model):
    product_code = models.CharField(max_length=50, unique=True)
    description = models.TextField()  # Mantener como TextField
    unit = models.CharField(max_length=20)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    min_stock = models.PositiveIntegerField(default=0)
    max_stock = models.IntegerField(default=0)
    location = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=100, blank=True)
    current_stock = models.PositiveIntegerField(default=0)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Activo")  # Agregar este campo
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['product_code']

    def __str__(self):
        return f"{self.product_code} - {self.description[:50]}"

    # Método helper para compatibilidad
    def get_short_description(self):
        """Retorna una descripción corta para interfaces que esperan CharField"""
        return self.description[:100] if self.description else ""