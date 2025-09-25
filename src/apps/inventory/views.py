# src/apps/inventory/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .models import Product, Supplier, Warehouse  # <-- AÑADE Supplier y Warehouse AQUÍ
from .forms import ProductForm
from django.db.models import F, Sum, Avg, Count, Q  # <-- Simplifica los imports
from django.contrib import messages
from django.db.models.functions import Lower
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.views import View

def dashboard_view(request):
    # Estadísticas básicas
    total_products = Product.objects.count()
    low_stock_products_count = Product.objects.filter(
        current_stock__lte=F('min_stock'), 
        current_stock__gt=0
    ).count()
    out_of_stock_count = Product.objects.filter(current_stock=0).count()
    
    # Valor total del inventario
    total_value = Product.objects.aggregate(
        total=Sum(F('current_stock') * F('unit_price'))
    )['total'] or 0
    
    # Nuevas métricas
    average_stock = Product.objects.aggregate(
        avg=Avg('current_stock')
    )['avg'] or 0
    
    categories_count = Product.objects.exclude(
        Q(category__isnull=True) | Q(category='')
    ).values('category').distinct().count()
    
    suppliers_count = Supplier.objects.count()  # <-- Ahora funciona
    warehouses_count = Warehouse.objects.count()  # <-- Ahora funciona
    
    # Productos con stock bajo y sin stock
    low_stock_products = Product.objects.filter(
        current_stock__lte=F('min_stock'), 
        current_stock__gt=0
    )[:10]
    
    out_of_stock_products = Product.objects.filter(current_stock=0)[:10]
    
    context = {
        'total_products': total_products,
        'low_stock_products_count': low_stock_products_count,
        'out_of_stock_count': out_of_stock_count,
        'total_value': total_value,
        'average_stock': round(average_stock, 1),
        'categories_count': categories_count,
        'suppliers_count': suppliers_count,
        'warehouses_count': warehouses_count,
        'low_stock_products': {
            'count': low_stock_products_count,
            'products': low_stock_products
        },
        'out_of_stock_products': {
            'count': out_of_stock_count,
            'products': out_of_stock_products
        }
    }
    return render(request, 'inventory/dashboard.html', context)

class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'inventory/product_list.html'
    context_object_name = 'products'
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset().order_by(Lower('description'))
        
        # Filtro de búsqueda
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(description__icontains=query)
        
        # Filtro por categoría
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Filtro por estado de stock
        stock_status = self.request.GET.get('stock_status')
        if stock_status == 'low':
            queryset = queryset.filter(current_stock__lte=F('min_stock'))
        elif stock_status == 'out':
            queryset = queryset.filter(current_stock=0)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas
        context['total_products'] = Product.objects.count()
        context['low_stock_count'] = Product.objects.filter(current_stock__lte=F('min_stock'), current_stock__gt=0).count()
        context['out_of_stock_count'] = Product.objects.filter(current_stock=0).count()
        
        # Valor total del inventario
        total_value = Product.objects.aggregate(
            total=Sum(F('current_stock') * F('unit_price'))
        )['total'] or 0
        context['total_value'] = total_value
        
        # Categorías únicas para el filtro
        context['categories'] = Product.objects.exclude(category='').values_list('category', flat=True).distinct()
        
        return context

class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'inventory/product_detail.html'
    context_object_name = 'product'

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('inventory:list')

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('inventory:list')

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'inventory/product_confirm_delete.html'
    success_url = reverse_lazy('inventory:list')

class InventoryReportView(LoginRequiredMixin, TemplateView):
    template_name = 'inventory/report.html'

class InventoryReportPDFView(LoginRequiredMixin, View):
    """Vista básica para reporte PDF"""
    
    def get(self, request, *args, **kwargs):
        products = Product.objects.all()
        
        html_string = render_to_string('inventory/report_pdf.html', {
            'products': products
        })
        
        html = HTML(string=html_string)
        pdf = html.write_pdf()
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'filename="inventory_report.pdf"'
        return response
    
@login_required
def request_replenishment(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    # Implement actual notification logic
    try:
        # Example: Send email notification
        subject = f"Replenishment Request: {product.description}"
        message = f"Product {product.description} (SKU: {product.sku}) needs replenishment.\nCurrent stock: {product.current_stock}\nMinimum stock: {product.min_stock}"
        
        # Replace with your actual email sending logic
        # send_mail(subject, message, 'noreply@example.com', ['inventory@example.com'])
        
        messages.success(request, f'Solicitud de reabastecimiento para "{product.description}" enviada con éxito.')
    except Exception as e:
        messages.error(request, f'Error al enviar la solicitud: {str(e)}')
    
    return redirect('inventory:detail', pk=product.pk)

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Product

def product_detail_api(request, pk):
    """
    Vista de API que devuelve los detalles de un producto en formato JSON.
    Se utiliza para cargar dinámicamente la información del producto en el formulario de movimiento.
    """
    if request.method == 'GET':
        product = get_object_or_404(Product, pk=pk)
        data = {
            'current_stock': product.current_stock,
            'min_stock': product.min_stock,
            'location': product.location,
        }
        return JsonResponse(data)
    else:
        # Si no es una solicitud GET, devuelve un error 405 (Método no permitido)
        return JsonResponse({'error': 'Método no permitido'}, status=405)