from django.urls import path
from rest_framework import routers
from . import api_views

router = routers.DefaultRouter()
router.register(r'products', api_views.ProductViewSet)
router.register(r'suppliers', api_views.SupplierViewSet)
router.register(r'clients', api_views.ClientViewSet)
router.register(r'warehouses', api_views.WarehouseViewSet)
urlpatterns = router.urls

urlpatterns = [
    path('stock/', api_views.StockAPIView.as_view(), name='stock'),
    path('productos/buscar/', api_views.ProductSearchAPI.as_view(), name='product_search'),
    path('alertas-stock/', api_views.StockAlertsAPI.as_view(), name='stock_alerts'),
] + router.urls