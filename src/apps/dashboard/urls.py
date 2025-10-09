from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='index'),
    path('api/product-search/', views.product_search_api, name='product_search_api'),
    path('api/dashboard-stats/', views.dashboard_stats_api, name='dashboard_stats_api'),
    path('request_replenishment/<int:pk>/', views.request_replenishment, name='request_replenishment'),
]