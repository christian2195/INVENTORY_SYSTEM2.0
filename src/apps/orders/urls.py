# src/apps/orders/urls.py
from django.urls import path
from .views import (
    OrderListView,
    OrderCreateView,
    OrderUpdateView,
    OrderDetailView,
    OrderDeleteView,
    approve_order,
    deliver_order,
    cancel_order,
    get_product_price
)

app_name = 'orders'

urlpatterns = [
    path('', OrderListView.as_view(), name='list'),
    path('nuevo/', OrderCreateView.as_view(), name='create'),
    path('<int:pk>/editar/', OrderUpdateView.as_view(), name='update'),
    path('<int:pk>/', OrderDetailView.as_view(), name='detail'),
    path('<int:pk>/eliminar/', OrderDeleteView.as_view(), name='delete'),
    path('<int:pk>/aprobar/', approve_order, name='approve'),
    path('<int:pk>/entregar/', deliver_order, name='deliver'),
    path('<int:pk>/cancelar/', cancel_order, name='cancel'),
    path('api/producto/<int:product_id>/precio/', get_product_price, name='get_product_price'),
]