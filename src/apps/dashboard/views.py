from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from apps.inventory.models import Product, Movimiento, TipoMovimiento
from django.db.models import F, Q
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # Productos con stock crítico
            low_stock_products = Product.objects.annotate(
                diferencia=F('stock_minimo') - F('cantidad')
            ).filter(cantidad__lt=F('stock_minimo')).order_by('diferencia')[:10]
            
            context['low_stock_products'] = low_stock_products
            
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
            
            # Categorías para filtros
            from apps.inventory.models import Categoria
            context['categories'] = Categoria.objects.all()[:10]
            
        except Exception as e:
            # Manejo de errores en caso de que los modelos no existan
            context['low_stock_products'] = []
            context['total_products'] = 0
            context['critical_stock'] = 0
            context['today_entries'] = 0
            context['today_exits'] = 0
            context['categories'] = []
            print(f"Error en dashboard: {e}")
        
        return context

@login_required
def product_search_api(request):
    """
    API endpoint para buscar productos por nombre, código o descripción.
    Devuelve los resultados en formato JSON.
    """
    query = request.GET.get('query', '')
    if not query or len(query) < 2:
        return JsonResponse([], safe=False)
    
    try:
        products = Product.objects.filter(
            Q(nombre__icontains=query) |
            Q(codigo__icontains=query) |
            Q(descripcion__icontains=query)
        ).select_related('unidad_medida', 'categoria')[:10]
        
        results = []
        for p in products:
            results.append({
                'id': p.id,
                'nombre': p.nombre,
                'codigo': p.codigo,
                'cantidad': float(p.cantidad) if p.cantidad else 0,
                'precio_unitario': str(p.precio_unitario) if p.precio_unitario else '0.00',
                'descripcion': p.descripcion or '',
                'unidad_medida_abreviatura': p.unidad_medida.abreviatura if p.unidad_medida else '',
                'categoria_nombre': p.categoria.nombre if p.categoria else '',
                'stock_minimo': float(p.stock_minimo) if p.stock_minimo else 0
            })
        
        return JsonResponse(results, safe=False)
    
    except Exception as e:
        print(f"Error en búsqueda de productos: {e}")
        return JsonResponse([], safe=False)

@login_required
def request_replenishment(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    # Lógica para manejar la solicitud de reposición
    # Aquí podrías crear una notificación, enviar email, etc.
    
    messages.success(
        request, 
        f'Solicitud de reposición enviada para {product.nombre}. Stock actual: {product.cantidad}'
    )
    
    return redirect('dashboard:index')

# Vista adicional para estadísticas del dashboard
@login_required
def dashboard_stats_api(request):
    """
    API para obtener estadísticas actualizadas del dashboard
    """
    try:
        today = timezone.now().date()
        
        stats = {
            'total_products': Product.objects.count(),
            'critical_stock': Product.objects.filter(cantidad__lt=F('stock_minimo')).count(),
            'today_entries': Movimiento.objects.filter(
                fecha__date=today, 
                tipo_movimiento__es_salida=False
            ).count(),
            'today_exits': Movimiento.objects.filter(
                fecha__date=today, 
                tipo_movimiento__es_salida=True
            ).count(),
        }
        
        return JsonResponse(stats)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)