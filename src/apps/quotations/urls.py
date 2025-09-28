# src/apps/quotations/urls.py
from django.urls import path
from .views import (
    QuotationListView,
    QuotationDetailView,
    QuotationCreateView,
    QuotationUpdateView,
    change_quotation_status,
    convert_to_dispatch,
    get_product_price,
)

app_name = 'quotations'

urlpatterns = [
    path('', QuotationListView.as_view(), name='list'),
    path('nuevo/', QuotationCreateView.as_view(), name='create'),
    path('<int:pk>/', QuotationDetailView.as_view(), name='detail'),
    path('editar/<int:pk>/', QuotationUpdateView.as_view(), name='update'),
    path('<int:pk>/estado/<str:status>/', change_quotation_status, name='change_status'),
    path('<int:pk>/convertir-despacho/', convert_to_dispatch, name='convert_to_dispatch'),
    path('api/producto/<int:product_id>/precio/', get_product_price, name='get_product_price'),
]