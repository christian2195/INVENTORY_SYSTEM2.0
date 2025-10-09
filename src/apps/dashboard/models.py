from django.db import models
from django.db.models import F

class ProductManager(models.Manager):
    def get_low_stock_products(self, limit=10):
        """
        Obtiene los productos cuyo stock actual es menor que el stock mínimo.
        """
        return self.get_queryset().annotate(
            difference=F('stock_minimo') - F('cantidad')
        ).filter(cantidad__lt=F('stock_minimo')).order_by('difference')[:limit]

class DashboardSetting(models.Model):
    name = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Configuración del Dashboard"
        verbose_name_plural = "Configuraciones del Dashboard"