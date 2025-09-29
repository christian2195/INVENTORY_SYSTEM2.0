# src/apps/orders/views.py
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.forms import inlineformset_factory
from .models import Order, OrderItem
from .forms import OrderForm, OrderItemForm, OrderItemFormSet
from apps.inventory.models import Product
from apps.movements.models import Movement

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset().select_related('client', 'supplier', 'created_by')
        
        # Filtros
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        client = self.request.GET.get('client')
        if client:
            queryset = queryset.filter(client_id=client)
            
        return queryset.order_by('-order_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.inventory.models import Client
        context['clients'] = Client.objects.all().order_by('name')
        context['status_choices'] = Order.ORDER_STATUS_CHOICES
        return context

class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'
    success_url = reverse_lazy('orders:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = OrderItemFormSet(self.request.POST)
        else:
            context['formset'] = OrderItemFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.created_by = self.request.user
            self.object.save()

            if formset.is_valid():
                formset.instance = self.object
                formset.save()
                
                # Calcular total
                self.object.calculate_total()
            else:
                return self.form_invalid(form)

        messages.success(self.request, f'✅ Orden #{self.object.order_number} creada exitosamente.')
        return redirect(self.get_success_url())

class OrderUpdateView(LoginRequiredMixin, UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'
    
    def get_success_url(self):
        return reverse_lazy('orders:detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = OrderItemFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = OrderItemFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        if not self.object.is_editable:
            messages.error(self.request, '❌ No se puede editar una orden que no está pendiente.')
            return redirect('orders:detail', pk=self.object.pk)
        
        with transaction.atomic():
            self.object = form.save()
            
            if formset.is_valid():
                formset.instance = self.object
                formset.save()
                
                # Recalcular total
                self.object.calculate_total()
            else:
                return self.form_invalid(form)

        messages.success(self.request, f'✅ Orden #{self.object.order_number} actualizada exitosamente.')
        return redirect(self.get_success_url())

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.select_related('product')
        return context

class OrderDeleteView(LoginRequiredMixin, DeleteView):
    model = Order
    template_name = 'orders/order_confirm_delete.html'
    success_url = reverse_lazy('orders:list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.is_editable:
            messages.error(request, '❌ No se puede eliminar una orden que no está pendiente.')
            return redirect('orders:detail', pk=self.object.pk)
            
        messages.success(request, f'✅ Orden #{self.object.order_number} eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)

@transaction.atomic
def approve_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.status == 'PENDING':
        order.status = 'APPROVED'
        order.save()
        messages.success(request, f'✅ Orden #{order.order_number} aprobada exitosamente.')
    else:
        messages.error(request, '❌ La orden no puede ser aprobada en su estado actual.')
    return redirect('orders:detail', pk=pk)

@transaction.atomic
def deliver_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.status == 'APPROVED':
        order.status = 'DELIVERED'
        order.save()

        # Registrar movimientos de inventario
        for item in order.items.all():
            Movement.objects.create(
                product=item.product,
                movement_type='IN',  # Entrada por compra
                quantity=item.quantity,
                unit_price=item.unit_price,
                reference_number=order.order_number,
                notes=f'Orden de compra #{order.order_number}',
                created_by=request.user
            )
        messages.success(request, f'✅ Orden #{order.order_number} marcada como entregada y movimientos registrados.')
    else:
        messages.error(request, '❌ La orden debe estar aprobada para poder entregarse.')
    return redirect('orders:detail', pk=pk)

@transaction.atomic
def cancel_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.status in ['PENDING', 'APPROVED']:
        order.status = 'CANCELLED'
        order.save()
        messages.success(request, f'✅ Orden #{order.order_number} cancelada exitosamente.')
    else:
        messages.error(request, '❌ No se puede cancelar una orden ya entregada.')
    return redirect('orders:detail', pk=pk)

def get_product_price(request, product_id):
    """API para obtener el precio de un producto"""
    product = get_object_or_404(Product, id=product_id)
    return JsonResponse({
        'price': str(product.unit_price or 0),
        'unit_measure': getattr(product, 'unit', '') or getattr(product, 'unit_measure', '') or 'unidad'
    })