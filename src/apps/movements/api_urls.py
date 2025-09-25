# src/apps/movements/api_urls.py
from rest_framework import routers
from . import api_views

router = routers.DefaultRouter()
router.register(r'movements', api_views.MovementViewSet)

urlpatterns = router.urls