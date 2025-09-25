# src/apps/dispatch_notes/models.py
from django.db import models
from django.utils import timezone
from apps.inventory.models import Product, Client, Supplier
from django.contrib.auth.models import User
from django.db.models import F
import random
import string

class DispatchNote(models.Model):
    DISPATCH_STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('DISPATCHED', 'Despachado'),
        ('CANCELLED', 'Cancelado'),
    ]

    # Cambiar a blank=True para generación automática
    dispatch_number = models.CharField(max_length=50, unique=True, verbose_name="Número de Despacho", blank=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Cliente")
    beneficiary = models.CharField(max_length=200, blank=True, verbose_name="Nombre del Beneficiario")
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Proveedor")
    order_number = models.CharField(max_length=50, blank=True, verbose_name="N° de Orden Asociada")
    dispatch_date = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Despacho")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Creado por")
    status = models.CharField(max_length=20, choices=DISPATCH_STATUS_CHOICES, default='PENDING', verbose_name="Estado")
    notes = models.TextField(blank=True, verbose_name="Observaciones")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False, verbose_name="Total")
    
    # Campos del transporte
    driver_name = models.CharField(max_length=100, blank=True, verbose_name="Nombre del Conductor")
    driver_id = models.CharField(max_length=20, blank=True, verbose_name="C.I. del Conductor")
    vehicle_type = models.CharField(max_length=100, blank=True, verbose_name="Tipo de Vehículo")
    vehicle_color = models.CharField(max_length=50, blank=True, verbose_name="Color del Vehículo")
    license_plate = models.CharField(max_length=20, blank=True, verbose_name="Placa")

    class Meta:
        verbose_name = "Nota de Despacho"
        verbose_name_plural = "Notas de Despacho"
        ordering = ['-dispatch_date']

    def __str__(self):
        return f'Nota de Despacho #{self.dispatch_number}'

    def save(self, *args, **kwargs):
        # Generar número automático si no existe
        if not self.dispatch_number:
            self.dispatch_number = self.generate_dispatch_number()
        super().save(*args, **kwargs)

    def generate_dispatch_number(self):
        """Genera un número de despacho automático con formato ND-YYYYMMDD-XXXX"""
        date_str = timezone.now().strftime('%Y%m%d')
        
        # Contar despachos del día
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timezone.timedelta(days=1)
        
        today_count = DispatchNote.objects.filter(
            dispatch_date__gte=today_start,
            dispatch_date__lt=today_end
        ).count()
        
        sequence = today_count + 1
        return f"ND-{date_str}-{sequence:04d}"

class DispatchItem(models.Model):
    dispatch_note = models.ForeignKey(DispatchNote, related_name='items', on_delete=models.CASCADE, verbose_name="Nota de Despacho")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Producto")
    quantity = models.PositiveIntegerField(verbose_name="Cantidad")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Precio Unitario")
    brand = models.CharField(max_length=100, blank=True, verbose_name="Marca")
    model = models.CharField(max_length=100, blank=True, verbose_name="Modelo")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, editable=False, verbose_name="Subtotal")
    
    class Meta:
        verbose_name = "Artículo de Despacho"
        verbose_name_plural = "Artículos de Despacho"

    def save(self, *args, **kwargs):
        if self.unit_price and self.quantity:
            self.subtotal = self.quantity * self.unit_price
        else:
            self.subtotal = 0
        super().save(*args, **kwargs)
        
        # Actualizar el total de la nota de despacho
        if self.dispatch_note:
            total = sum(item.subtotal for item in self.dispatch_note.items.all())
            DispatchNote.objects.filter(pk=self.dispatch_note.pk).update(total=total)
