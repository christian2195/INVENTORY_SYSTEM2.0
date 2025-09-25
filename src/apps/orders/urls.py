# src/apps/orders/urls.py
from django.urls import path
from .views import (
    OrderListView,
    OrderCreateView,
    OrderDetailView,
    approve_order,
    deliver_order
)

app_name = 'orders'

urlpatterns = [
    path('', OrderListView.as_view(), name='list'),
    path('nuevo/', OrderCreateView.as_view(), name='create'),
    path('<int:pk>/', OrderDetailView.as_view(), name='detail'),
    path('<int:pk>/aprobar/', approve_order, name='approve'),
    path('<int:pk>/entregar/', deliver_order, name='deliver'),
]