# src/apps/reception_notes/api_urls.py
from rest_framework import routers
from . import api_views

router = routers.DefaultRouter()
router.register(r'reception-notes', api_views.ReceptionNoteViewSet)
router.register(r'items', api_views.ReceptionItemViewSet)

urlpatterns = router.urls