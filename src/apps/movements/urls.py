# apps/movements/urls.py
from django.urls import path
from . import views

app_name = 'movements'

urlpatterns = [
    # Movimientos generales
    path('', views.MovementListView.as_view(), name='list'),
    path('nuevo/', views.MovementCreateView.as_view(), name='create'),
    path('editar/<int:pk>/', views.MovementUpdateView.as_view(), name='update'),
    path('eliminar/<int:pk>/', views.MovementDeleteView.as_view(), name='delete'),
    
    # Vistas específicas
    path('entradas/', views.EntryListView.as_view(), name='entry_list'),
    path('salidas/', views.ExitListView.as_view(), name='exit_list'),
    
    # API para información de productos
    path('api/product/<int:product_id>/', views.product_info_api, name='product_info_api'),
]