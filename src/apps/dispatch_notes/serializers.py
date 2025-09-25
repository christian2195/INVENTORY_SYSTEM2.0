# En tu archivo serializers.py (si no existe, créalo)
from rest_framework import serializers
from apps.inventory.models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'product_code', 'description', 'unit_price', 'current_stock', 'brand', 'model', 'category']