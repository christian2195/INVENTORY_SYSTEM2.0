# apps/movements/views.py
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Sum, Q
from django.http import JsonResponse

# Solo importa Movement
from .models import Movement
from .forms import MovementForm

class MovementListView(LoginRequiredMixin, ListView):
    model = Movement
    template_name = 'movements/movement_list.html'
    context_object_name = 'movements'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Movement.objects.select_related('product', 'created_by').order_by('-date')
        
        # Filtros
        movement_type = self.request.GET.get('type')
        if movement_type:
            queryset = queryset.filter(movement_type=movement_type)
            
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(product__description__icontains=search_query) |
                Q(observations__icontains=search_query) |
                Q(delivered_to__icontains=search_query)
            )
            
        # Filtro por fecha
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        
        # Estadísticas para el template
        context['total_movements'] = queryset.count()
        context['entries_count'] = queryset.filter(movement_type='IN').count()
        context['exits_count'] = queryset.filter(movement_type='OUT').count()
        
        # Calcular valores totales
        total_entries = queryset.filter(movement_type='IN').aggregate(
            total=Sum('quantity')
        )['total'] or 0
        
        total_exits = queryset.filter(movement_type='OUT').aggregate(
            total=Sum('quantity')
        )['total'] or 0
        
        total_value = sum(movement.quantity * movement.unit_price for movement in queryset)
        
        context['total_quantity'] = total_entries + total_exits
        context['total_value'] = total_value
        
        # Pasar parámetros de filtro al template
        context['current_filters'] = {
            'type': self.request.GET.get('type', ''),
            'q': self.request.GET.get('q', ''),
            'start_date': self.request.GET.get('start_date', ''),
            'end_date': self.request.GET.get('end_date', ''),
        }
        
        return context

class MovementCreateView(LoginRequiredMixin, CreateView):
    model = Movement
    form_class = MovementForm
    template_name = 'movements/movement_form.html'
    success_url = reverse_lazy('movements:list')
    
    def get_initial(self):
        """Pre-seleccionar tipo de movimiento si viene por URL"""
        initial = super().get_initial()
        movement_type = self.request.GET.get('type')
        if movement_type in ['IN', 'OUT']:
            initial['movement_type'] = movement_type
        return initial
    
    def form_valid(self, form):
        try:
            # Asignar el usuario actual
            form.instance.created_by = self.request.user
            result = super().form_valid(form)
            messages.success(self.request, "Movimiento registrado correctamente.")
            return result
        except ValidationError as e:
            # Mostrar error de validación
            form.add_error(None, e)
            return self.form_invalid(form)
        except Exception as e:
            # Mostrar error general
            messages.error(self.request, f"Error al guardar el movimiento: {str(e)}")
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "Por favor, corrija los errores en el formulario.")
        return super().form_invalid(form)

class MovementUpdateView(LoginRequiredMixin, UpdateView):
    model = Movement
    form_class = MovementForm
    template_name = 'movements/movement_form.html'
    success_url = reverse_lazy('movements:list')
    
    def form_valid(self, form):
        try:
            result = super().form_valid(form)
            messages.success(self.request, "Movimiento actualizado correctamente.")
            return result
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f"Error al actualizar el movimiento: {str(e)}")
            return self.form_invalid(form)

class MovementDeleteView(LoginRequiredMixin, DeleteView):
    model = Movement
    template_name = 'movements/movement_confirm_delete.html'
    success_url = reverse_lazy('movements:list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Movimiento eliminado correctamente.")
        return super().delete(request, *args, **kwargs)

# Vistas específicas para entradas y salidas
class EntryListView(LoginRequiredMixin, ListView):
    """Vista para listar solo entradas"""
    model = Movement
    template_name = 'movements/entry_list.html'
    context_object_name = 'entries'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Movement.objects.filter(movement_type='IN')\
            .select_related('product', 'created_by')\
            .order_by('-date')
            
        # Filtros
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(product__description__icontains=search_query) |
                Q(observations__icontains=search_query)
            )
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entries = self.get_queryset()
        
        # Calcular totales
        total_quantity = entries.aggregate(total=Sum('quantity'))['total'] or 0
        total_value = sum(entry.quantity * entry.unit_price for entry in entries)
        
        context['total_quantity'] = total_quantity
        context['total_value'] = total_value
        context['search_query'] = self.request.GET.get('q', '')
        
        return context

class ExitListView(LoginRequiredMixin, ListView):
    """Vista para listar solo salidas"""
    model = Movement
    template_name = 'movements/exit_list.html'
    context_object_name = 'exits'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Movement.objects.filter(movement_type='OUT')\
            .select_related('product', 'created_by')\
            .order_by('-date')
            
        # Filtros
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(product__description__icontains=search_query) |
                Q(observations__icontains=search_query) |
                Q(delivered_to__icontains=search_query)
            )
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exits = self.get_queryset()
        
        # Calcular totales
        total_quantity = exits.aggregate(total=Sum('quantity'))['total'] or 0
        total_value = sum(exit.quantity * exit.unit_price for exit in exits)
        
        context['total_quantity'] = total_quantity
        context['total_value'] = total_value
        context['search_query'] = self.request.GET.get('q', '')
        
        return context

# Vista para API de información de producto
def product_info_api(request, product_id):
    """API para obtener información del producto"""
    try:
        from apps.inventory.models import Product
        product = Product.objects.get(pk=product_id)
        
        return JsonResponse({
            'success': True,
            'current_stock': product.current_stock,
            'min_stock': product.min_stock,
            'location': product.location or '',
            'description': product.description
        })
    except Product.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Producto no encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def product_detail_api(request, pk):
    """
    Vista de API para obtener los detalles de un producto en formato JSON.
    """
    if request.method == 'GET':
        try:
            product = get_object_or_404(Product, pk=pk)
            data = {
                'current_stock': product.current_stock,
                'min_stock': product.min_stock,
                'location': product.location,
            }
            return JsonResponse(data)
        except Exception as e:
            # Manejo de errores en caso de que algo salga mal en la base de datos o el modelo
            return JsonResponse({'error': str(e)}, status=500)
    else:
        # Devuelve un error si no es un método GET
        return JsonResponse({'error': 'Método no permitido'}, status=405)