# src/apps/quotations/api_views.py
from rest_framework import viewsets
from .models import Quotation, QuotationItem
from .serializers import QuotationSerializer, QuotationItemSerializer

class QuotationViewSet(viewsets.ModelViewSet):
    queryset = Quotation.objects.all().order_by('-quotation_number')
    serializer_class = QuotationSerializer

class QuotationItemViewSet(viewsets.ModelViewSet):
    queryset = QuotationItem.objects.all()
    serializer_class = QuotationItemSerializer