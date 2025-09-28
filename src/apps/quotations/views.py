# src/apps/quotations/views.py
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone  # ✅ AGREGAR ESTA IMPORTACIÓN
from .models import Quotation, QuotationItem
from .forms import QuotationForm, QuotationItemFormSet

class QuotationListView(LoginRequiredMixin, ListView):
    model = Quotation
    template_name = 'quotations/quotation_list.html'
    context_object_name = 'quotations'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('client', 'dispatch_note')
        
        # Filtro por estado
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filtro por cliente
        client_id = self.request.GET.get('client')
        if client_id:
            queryset = queryset.filter(client_id=client_id)
            
        return queryset.order_by('-date_created')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.inventory.models import Client
        context['clients'] = Client.objects.all().order_by('name')
        context['status_choices'] = Quotation.STATUS_CHOICES
        return context

class QuotationDetailView(LoginRequiredMixin, DetailView):
    model = Quotation
    template_name = 'quotations/quotation_detail.html'
    context_object_name = 'quotation'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.select_related('product')
        return context

class QuotationCreateView(LoginRequiredMixin, CreateView):
    model = Quotation
    form_class = QuotationForm
    template_name = 'quotations/quotation_form.html'
    success_url = reverse_lazy('quotations:list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = QuotationItemFormSet(self.request.POST)
        else:
            context['formset'] = QuotationItemFormSet()
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        with transaction.atomic():
            # Asignar usuario creador
            self.object = form.save(commit=False)
            self.object.created_by = self.request.user
            
            # Guardar para generar número automático
            self.object.save()
            
            if formset.is_valid():
                # Filtrar forms vacíos
                instances = formset.save(commit=False)
                for instance in instances:
                    # Solo guardar si tiene producto y cantidad
                    if instance.product and instance.quantity > 0:
                        instance.save()
                
                # Eliminar los marcados para borrar
                for form in formset.deleted_forms:
                    if form.instance.pk:
                        form.instance.delete()
                        
                # Recalcular total
                self.object.save()
            else:
                return self.form_invalid(form)
        
        messages.success(self.request, f'Cotización {self.object.quotation_number} creada exitosamente.')
        return redirect(self.get_success_url())

class QuotationUpdateView(LoginRequiredMixin, UpdateView):
    model = Quotation
    form_class = QuotationForm
    template_name = 'quotations/quotation_form.html'
    success_url = reverse_lazy('quotations:list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = QuotationItemFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = QuotationItemFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        with transaction.atomic():
            self.object = form.save()
            
            if formset.is_valid():
                instances = formset.save(commit=False)
                for instance in instances:
                    if instance.product and instance.quantity > 0:
                        instance.save()
                
                for form in formset.deleted_forms:
                    if form.instance.pk:
                        form.instance.delete()
                        
                # Recalcular total
                self.object.save()
            else:
                return self.form_invalid(form)
        
        messages.success(self.request, f'Cotización {self.object.quotation_number} actualizada exitosamente.')
        return redirect(self.get_success_url())

def change_quotation_status(request, pk, status):
    """Vista para cambiar el estado de una cotización"""
    quotation = get_object_or_404(Quotation, pk=pk)
    
    if status in ['SENT', 'APPROVED', 'REJECTED']:
        quotation.status = status
        
        if status == 'SENT':
            # ✅ timezone ya está importado globalmente
            quotation.date_sent = timezone.now()
        elif status == 'APPROVED':
            # ✅ timezone ya está importado globalmente
            quotation.date_approved = timezone.now()
        
        quotation.save()
        messages.success(request, f'Estado de la cotización actualizado a {quotation.get_status_display()}.')
    
    return redirect('quotations:detail', pk=pk)

def convert_to_dispatch(request, pk):
    """Vista para convertir cotización en nota de despacho"""
    quotation = get_object_or_404(Quotation, pk=pk)
    
    if not quotation.can_convert_to_dispatch():
        messages.error(request, 'No se puede convertir esta cotización en despacho. Verifica que esté aprobada y no tenga ya un despacho asociado.')
        return redirect('quotations:detail', pk=pk)
    
    try:
        dispatch_note = quotation.convert_to_dispatch_note(request.user)
        if dispatch_note:
            messages.success(request, f'Cotización convertida en nota de despacho #{dispatch_note.dispatch_number}.')
            return redirect('dispatch_notes:detail', pk=dispatch_note.pk)
        else:
            messages.error(request, 'Error al convertir la cotización. No se pudo crear el despacho.')
    except Exception as e:
        messages.error(request, f'Error al convertir la cotización: {str(e)}')
    
    return redirect('quotations:detail', pk=pk)

def get_product_price(request, product_id):
    """API para obtener el precio de un producto"""
    from apps.inventory.models import Product
    try:
        product = Product.objects.get(id=product_id)
        
        # Intentar diferentes nombres de campo de precio
        price_fields = ['unit_price', 'price', 'sale_price', 'cost_price']
        price = 0
        
        for field in price_fields:
            if hasattr(product, field):
                price = getattr(product, field)
                break
        
        return JsonResponse({
            'price': float(price),
            'product_code': product.product_code,
            'description': product.description
        })
        
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'Error interno: {str(e)}'}, status=500)