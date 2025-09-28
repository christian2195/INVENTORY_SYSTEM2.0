# src/apps/reception_notes/models.py
from django.db import models
from django.utils import timezone
from django.db.models import Max
from apps.inventory.models import Product, Supplier
from django.contrib.auth.models import User
from django.db.models import F

class ReceptionNote(models.Model):
    RECEIPT_STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('RECEIVED', 'Recibida'),
        ('CANCELLED', 'Cancelada'),
    ]
    
    receipt_number = models.CharField(max_length=50, unique=True, verbose_name="Número de Nota", editable=False)
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

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            # Generar número automático: REC-YYYY-MM-NNNN
            current_year = timezone.now().year
            current_month = timezone.now().month
            
            # Obtener el último número del mes actual
            last_note = ReceptionNote.objects.filter(
                receipt_date__year=current_year,
                receipt_date__month=current_month
            ).aggregate(Max('receipt_number'))
            
            if last_note['receipt_number__max']:
                try:
                    last_number = int(last_note['receipt_number__max'].split('-')[-1])
                    new_number = last_number + 1
                except (ValueError, IndexError):
                    new_number = 1
            else:
                new_number = 1
                
            self.receipt_number = f"REC-{current_year}-{current_month:02d}-{new_number:04d}"
        
        super().save(*args, **kwargs)

    def update_total(self):
        """Actualizar el total basado en los items"""
        total = self.items.aggregate(total=models.Sum(models.F('quantity') * models.F('unit_price')))['total']
        self.total = total or 0
        self.save(update_fields=['total'])

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
        
        # Actualizar el total de la nota de recepción
        if self.receipt_note:
            self.receipt_note.update_total()
        
        # Actualizar stock al guardar un nuevo ítem de recepción (solo si la recepción está validada)
        if self.pk is None and self.receipt_note.status == 'RECEIVED':
            self.product.current_stock = F('current_stock') + self.quantity
            self.product.save(update_fields=['current_stock'])