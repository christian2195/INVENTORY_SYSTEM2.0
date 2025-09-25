from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.inventory.models import Product, Movimiento, TipoMovimiento, Proveedor, Almacen, Cliente, Cotizacion # Asegúrate de importar los modelos necesarios
from apps.movements.models import Movement  # Asumiendo que esta es la app de movimientos
from django.db.models import F, Sum, Q
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import F

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Productos con stock crítico
        # Asumiendo que el modelo Producto tiene un manager 'objects' con este método
        context['low_stock_products'] = Product.objects.get_low_stock_products()
        
        # Estadísticas
        context['total_products'] = Product.objects.count()
        context['critical_stock'] = Product.objects.filter(
            cantidad__lt=F('stock_minimo')
        ).count()
        
        # Movimientos del día
        today = timezone.now().date()
        context['today_entries'] = Movimiento.objects.filter(
            fecha__date=today,
            tipo_movimiento__es_salida=False
        ).count()
        context['today_exits'] = Movimiento.objects.filter(
            fecha__date=today,
            tipo_movimiento__es_salida=True
        ).count()
        
        return context

# Nueva vista para el buscador de productos (API)
def product_search_api(request):
    """
    API endpoint para buscar productos por nombre, código o descripción.
    Devuelve los resultados en formato JSON.
    """
    query = request.GET.get('query', '')
    if not query:
        return JsonResponse([], safe=False)
    
    products = Product.objects.filter(
        Q(nombre__icontains=query) |
        Q(codigo__icontains=query) |
        Q(descripcion__icontains=query)
    ).select_related('unidad_medida', 'categoria')[:10]  # Limitar a 10 resultados para rendimiento
    
    results = [
        {
            'id': p.id,
            'nombre': p.nombre,
            'codigo': p.codigo,
            'cantidad': p.cantidad,
            'precio_unitario': str(p.precio_unitario) if p.precio_unitario is not None else '0.00',
            'descripcion': p.descripcion,
            'unidad_medida_abreviatura': p.unidad_medida.abreviatura if p.unidad_medida else '',
            'categoria_nombre': p.categoria.nombre if p.categoria else ''
        } for p in products
    ]
    
    return JsonResponse(results, safe=False)

def request_replenishment(request, pk):
    product = get_object_or_404(Product, pk=pk)
    # Lógica para manejar la solicitud de reposición (ej. crear una notificación)
    # ...
    # Puedes añadir un mensaje de éxito si lo deseas
    return redirect('dashboard:index')
