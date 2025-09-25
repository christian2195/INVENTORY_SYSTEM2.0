# src/apps/quotations/api_urls.py
from rest_framework import routers
from . import api_views

router = routers.DefaultRouter()
router.register(r'quotations', api_views.QuotationViewSet)
router.register(r'items', api_views.QuotationItemViewSet)

urlpatterns = router.urls