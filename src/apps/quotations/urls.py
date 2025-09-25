# src/apps/quotations/urls.py
from django.urls import path
from .views import (
    QuotationListView,
    QuotationDetailView,
    QuotationCreateView,
    QuotationUpdateView,
)

app_name = 'quotations'

urlpatterns = [
    path('', QuotationListView.as_view(), name='list'),
    path('nuevo/', QuotationCreateView.as_view(), name='create'),
    path('<int:pk>/', QuotationDetailView.as_view(), name='detail'),
    path('editar/<int:pk>/', QuotationUpdateView.as_view(), name='update'),
    # Los demás paths como 'approve' se pueden añadir más tarde
]