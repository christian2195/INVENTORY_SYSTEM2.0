# apps/movements/models.py
from django.db import models
from django.utils import timezone
from apps.inventory.models import Product
from django.contrib.auth.models import User
from django.db.models import F
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

class Movement(models.Model):
    MOVEMENT_TYPES = [
        ('IN', 'Entrada'),
        ('OUT', 'Salida'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Producto")
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPES, verbose_name="Tipo de Movimiento")
    quantity = models.PositiveIntegerField(verbose_name="Cantidad", validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Precio Unitario",
        validators=[MinValueValidator(0)]
    )
    date = models.DateTimeField(default=timezone.now, verbose_name="Fecha")
    observations = models.TextField(blank=True, verbose_name="Observaciones")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Creado por")
    delivered_to = models.CharField(max_length=255, null=True, blank=True, verbose_name="Entregado a")

    def __str__(self):
        return f'{self.product.description} - {self.get_movement_type_display()}'

    @property
    def total_value(self):
        """Calcula el valor total del movimiento"""
        return self.quantity * self.unit_price

    def clean(self):
        """
        Validación adicional para evitar stock negativo
        """
        if self.movement_type == 'OUT' and self.product:
            if self.quantity > self.product.current_stock:
                raise ValidationError(
                    f"No hay suficiente stock de {self.product.description}. "
                    f"Stock disponible: {self.product.current_stock}, "
                    f"Intenta sacar: {self.quantity}"
                )
    
    def save(self, *args, **kwargs):
        """
        Sobrescribir save para validar antes de guardar y actualizar stock de forma segura
        """
        # Validar antes de guardar
        self.clean()
        
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Actualizar stock del producto de forma segura
        if is_new:
            product = self.product
            if self.movement_type == 'IN':
                # Usar F() expression para actualización atómica
                Product.objects.filter(pk=product.pk).update(
                    current_stock=F('current_stock') + self.quantity
                )
            elif self.movement_type == 'OUT':
                # Verificar nuevamente antes de actualizar (doble verificación)
                product.refresh_from_db()
                if self.quantity <= product.current_stock:
                    Product.objects.filter(pk=product.pk).update(
                        current_stock=F('current_stock') - self.quantity
                    )
                else:
                    # Revertir el movimiento si no hay suficiente stock
                    self.delete()
                    raise ValidationError(
                        f"Stock insuficiente después de validación. "
                        f"Stock actual: {product.current_stock}, "
                        f"Intenta sacar: {self.quantity}"
                    )