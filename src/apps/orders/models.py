# src/apps/orders/models.py
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.inventory.models import Product, Supplier, Client
from django.contrib.auth.models import User

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('PENDING', '🟡 Pendiente'),
        ('APPROVED', '🟢 Aprobado'),
        ('DELIVERED', '🔵 Entregado'),
        ('CANCELLED', '🔴 Cancelado'),
    ]

    order_number = models.CharField(max_length=50, unique=True, verbose_name="Número de Orden")
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Cliente")
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Proveedor")
    order_date = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Orden")
    delivery_date = models.DateField(null=True, blank=True, verbose_name="Fecha de Entrega Esperada")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Creado por")
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='PENDING', verbose_name="Estado")
    notes = models.TextField(blank=True, verbose_name="Observaciones")
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False, verbose_name="Total")
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado en")

    class Meta:
        verbose_name = "Orden de Compra"
        verbose_name_plural = "Órdenes de Compra"
        ordering = ['-order_date']

    def __str__(self):
        return f'Orden #{self.order_number}'

    def clean(self):
        if self.delivery_date and self.delivery_date < timezone.now().date():
            raise ValidationError({'delivery_date': 'La fecha de entrega no puede ser en el pasado.'})

    def save(self, *args, **kwargs):
        # Generar número de orden automático si no existe
        if not self.order_number:
            self.order_number = self.generate_order_number()
        
        super().save(*args, **kwargs)
        # Recalcular total después de guardar
        self.calculate_total()

    def generate_order_number(self):
        """Genera un número de orden automático en formato ORD-YYYY-NNNN"""
        current_year = timezone.now().year
        last_order = Order.objects.filter(
            order_number__startswith=f'ORD-{current_year}-'
        ).order_by('-order_number').first()
        
        if last_order:
            try:
                last_number = int(last_order.order_number.split('-')[-1])
                next_number = last_number + 1
            except (ValueError, IndexError):
                next_number = 1
        else:
            next_number = 1
        
        return f'ORD-{current_year}-{next_number:04d}'

    def calculate_total(self):
        """Calcula el total de la orden"""
        total = sum(item.subtotal for item in self.items.all())
        if self.total != total:
            self.total = total
            super().save(update_fields=['total'])

    @property
    def is_editable(self):
        """Determina si la orden puede ser editada"""
        return self.status in ['PENDING']

    @property
    def status_badge_class(self):
        """Retorna la clase CSS para el badge de estado"""
        status_classes = {
            'PENDING': 'bg-warning',
            'APPROVED': 'bg-success',
            'DELIVERED': 'bg-info',
            'CANCELLED': 'bg-danger',
        }
        return status_classes.get(self.status, 'bg-secondary')

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name="Orden")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Producto")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Cantidad")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Unitario")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False, verbose_name="Subtotal")

    class Meta:
        verbose_name = "Ítem de Orden"
        verbose_name_plural = "Ítems de Orden"

    def __str__(self):
        return f'{self.product.name} - {self.quantity} x ${self.unit_price}'

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError({'quantity': 'La cantidad debe ser mayor a cero.'})
        if self.unit_price <= 0:
            raise ValidationError({'unit_price': 'El precio unitario debe ser mayor a cero.'})

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        # Recalcular el total de la orden
        if self.order:
            self.order.calculate_total()