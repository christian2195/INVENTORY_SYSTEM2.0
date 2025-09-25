# src/core/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from apps.inventory import dashboard_views
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/dashboard/', dashboard_views.custom_dashboard, name='custom_dashboard'),
    
     # Redirecciona la URL raíz a la URL del dashboard de inventario
    path('', RedirectView.as_view(pattern_name='inventory:inventory_dashboard', permanent=False)),
    # URLs de autenticación de usuario
    path('accounts/', include('apps.users.urls')),
    
    # URLs de la API
    path('api/inventario/', include('apps.inventory.api_urls')),
    path('api/movimientos/', include('apps.movements.api_urls')),
    path('api/cotizaciones/', include('apps.quotations.api_urls')),
    path('api/notas-recepcion/', include('apps.reception_notes.api_urls')),
    path('notas-recepcion/', include('apps.reception_notes.urls')),
    
    # URLs de la aplicación web
    path('inventario/', include('apps.inventory.urls', namespace='inventory')),
    path('cotizaciones/', include('apps.quotations.urls')),
    path('pedidos/', include('apps.orders.urls')),
    path('movimientos/', include('apps.movements.urls')),
    path('devoluciones/', include('apps.returns.urls')),
    path('accounts/', include('apps.users.urls')),
    path('notas-despacho/', include('apps.dispatch_notes.urls')),
    path('users/', include('apps.users.urls', namespace='users')),
    # URLs de utilidades y error

    path('404/', views.page_not_found, name='404'),
    path('500/', views.server_error, name='500'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
