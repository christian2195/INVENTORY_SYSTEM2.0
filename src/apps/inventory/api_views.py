# src/apps/inventory/api_views.py
from rest_framework import viewsets, views
from rest_framework.response import Response
from rest_framework import status
from django.db.models import F
from .models import Product, Supplier, Client, Warehouse
from .serializers import ProductSerializer, SupplierSerializer, ClientSerializer, WarehouseSerializer
from django.db.models.functions import Lower

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer

class StockAPIView(views.APIView):
    def get(self, request):
        products = Product.objects.all().order_by('description')
        data = [
            {
                'product_code': product.product_code,
                'description': product.description,
                'current_stock': product.current_stock,
                'min_stock': product.min_stock,
                'status': 'OK' if product.current_stock > product.min_stock else 'LOW STOCK'
            }
            for product in products
        ]
        return Response(data)

class ProductSearchAPI(views.APIView):
    def get(self, request):
        query = request.query_params.get('q', '')
        if query:
            products = Product.objects.filter(
                description__icontains=query
            ).annotate(
                value=F('product_code'),
                label=F('description')
            ).order_by('label')[:10]
            data = list(products.values('value', 'label'))
        else:
            data = []
        return Response(data)

class StockAlertsAPI(views.APIView):
    def get(self, request):
        low_stock_products = Product.objects.filter(current_stock__lte=F('min_stock'))
        serializer = ProductSerializer(low_stock_products, many=True)
        return Response(serializer.data)