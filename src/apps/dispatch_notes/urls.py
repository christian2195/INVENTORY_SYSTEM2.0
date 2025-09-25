# src/apps/dispatch_notes/urls.py
from django.urls import path
from . import views

app_name = 'dispatch_notes'

urlpatterns = [
    path('', views.DispatchNoteListView.as_view(), name='list'),
    path('nuevo/', views.DispatchNoteCreateView.as_view(), name='create'),
    path('<int:pk>/', views.DispatchNoteDetailView.as_view(), name='detail'),
    path('editar/<int:pk>/', views.DispatchNoteUpdateView.as_view(), name='update'),
    path('imprimir/<int:pk>/', views.DispatchNotePrintView.as_view(), name='print'),
    path('despachar/<int:pk>/', views.dispatch_note_confirm, name='confirm_dispatch'),
    #path('products/<int:pk>/', views.ProductDetailAPIView.as_view(), name='product-detail-api'),
    path('api/product-search/', views.product_search_api, name='product_search_api'),
    path('cancelar/<int:pk>/', views.dispatch_note_cancel, name='cancel_dispatch'),
    path('api/client-data/<int:client_id>/', views.client_data_api, name='client_data_api'),
    
]