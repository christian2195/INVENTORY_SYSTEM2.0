# src/apps/orders/views.py
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Order, OrderItem
from .forms import OrderForm, OrderItemFormSet
from apps.inventory.models import Product, Client, Supplier
from apps.movements.models import Movement

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 15

    def get_queryset(self):
        return super().get_queryset().order_by('-order_date')

class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'

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
            else:
                return self.form_invalid(form)

        messages.success(self.request, 'Orden de compra creada con éxito.')
        return redirect(reverse_lazy('orders:list'))

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.all()
        return context

@transaction.atomic
def approve_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.status == 'PENDING':
        order.status = 'APPROVED'
        order.save()
        messages.success(request, 'Orden de compra aprobada con éxito.')
        return redirect('orders:detail', pk=pk)
    messages.error(request, 'La orden no puede ser aprobada en su estado actual.')
    return redirect('orders:detail', pk=pk)

@transaction.atomic
def deliver_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.status == 'APPROVED':
        order.status = 'DELIVERED'
        order.save()

        for item in order.items.all():
            Movement.objects.create(
                product=item.product,
                movement_type='OUT',
                quantity=item.quantity,
                unit_price=item.unit_price,
                delivered_to=order.client,
                notes=f'Orden de venta #{order.order_number}',
                created_by=request.user
            )
        messages.success(request, 'Orden de compra marcada como entregada y movimientos registrados.')
        return redirect('orders:detail', pk=pk)
    messages.error(request, 'La orden no puede ser entregada en su estado actual.')
    return redirect('orders:detail', pk=pk)