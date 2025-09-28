# src/apps/returns/models.py
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.dispatch_notes.models import DispatchNote, DispatchItem
from apps.inventory.models import Product, Client
from django.contrib.auth.models import User
from django.db.models import F

class ReturnNote(models.Model):
    RETURN_STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('RETURNED', 'Devuelta'),
        ('CANCELLED', 'Cancelada'),
    ]

    return_number = models.CharField(max_length=50, unique=True, verbose_name="Número de Devolución", editable=False)
    dispatch_note = models.ForeignKey(DispatchNote, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Nota de Despacho Original")
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Cliente")
    return_date = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Devolución")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Creado por")
    status = models.CharField(max_length=20, choices=RETURN_STATUS_CHOICES, default='PENDING', verbose_name="Estado")
    notes = models.TextField(blank=True, verbose_name="Observaciones")

    class Meta:
        verbose_name = "Nota de Devolución"
        verbose_name_plural = "Notas de Devolución"

    def __str__(self):
        return f'Nota de Devolución #{self.return_number}'

    def save(self, *args, **kwargs):
        if not self.return_number:
            # Generar número automático
            self.return_number = self.generate_return_number()
        super().save(*args, **kwargs)

    def generate_return_number(self):
        """Genera un número de devolución automático en formato DEV-YYYY-NNNN"""
        current_year = timezone.now().year
        
        # Obtener la última devolución del año actual
        last_return = ReturnNote.objects.filter(
            return_number__startswith=f'DEV-{current_year}-'
        ).order_by('-return_number').first()
        
        if last_return:
            try:
                # Extraer el número secuencial y incrementarlo
                last_number = int(last_return.return_number.split('-')[-1])
                next_number = last_number + 1
            except (ValueError, IndexError):
                next_number = 1
        else:
            next_number = 1
        
        # Formatear el número con ceros a la izquierda
        return f'DEV-{current_year}-{next_number:04d}'

class ReturnItem(models.Model):
    return_note = models.ForeignKey(ReturnNote, related_name='items', on_delete=models.CASCADE, verbose_name="Nota de Devolución")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Producto")
    quantity = models.PositiveIntegerField(verbose_name="Cantidad")
    
    class Meta:
        verbose_name = "Artículo de Devolución"
        verbose_name_plural = "Artículos de Devolución"