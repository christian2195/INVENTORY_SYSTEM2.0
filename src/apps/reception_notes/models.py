# src/apps/reception_notes/models.py
from django.db import models
from django.utils import timezone
from apps.inventory.models import Product, Supplier
from django.contrib.auth.models import User
from django.db.models import F

class ReceptionNote(models.Model):
    RECEIPT_STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('RECEIVED', 'Recibida'),
        ('CANCELLED', 'Cancelada'),
    ]
    
    receipt_number = models.CharField(max_length=50, unique=True, verbose_name="Número de Nota")
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Proveedor")
    receipt_date = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Recepción")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Creado por")
    status = models.CharField(max_length=20, choices=RECEIPT_STATUS_CHOICES, default='PENDING', verbose_name="Estado")
    notes = models.TextField(blank=True, verbose_name="Observaciones")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False, verbose_name="Total")

    class Meta:
        verbose_name = "Nota de Recepción"
        verbose_name_plural = "Notas de Recepción"

    def __str__(self):
        return f'Nota de Recepción #{self.receipt_number}'

class ReceptionItem(models.Model):
    receipt_note = models.ForeignKey(ReceptionNote, related_name='items', on_delete=models.CASCADE, verbose_name="Nota de Recepción")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Producto")
    quantity = models.PositiveIntegerField(verbose_name="Cantidad")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Unitario")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False, verbose_name="Subtotal")
    
    class Meta:
        verbose_name = "Artículo de Recepción"
        verbose_name_plural = "Artículos de Recepción"

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        
        # Actualizar stock al guardar un nuevo ítem de recepción
        if self.pk is None:
            self.product.current_stock = F('current_stock') + self.quantity
            self.product.save(update_fields=['current_stock'])