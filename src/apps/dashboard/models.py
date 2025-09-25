from django.db import models
from django.db.models import F

class ProductManager(models.Manager):
    def get_low_stock_products(self, limit=10):
        """
        Obtiene los productos cuyo stock actual es menor que el stock mínimo.
        """
        return self.get_queryset().annotate(
            difference=F('min_stock') - F('current_stock')
        ).filter(current_stock__lt=F('min_stock')).order_by('difference')[:limit]

# En tu modelo Product, asocia el nuevo manager
# class Product(models.Model):
#     ...
#     objects = ProductManager()
#     ...