# src/apps/reception_notes/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db import transaction
from django.db.models import F
from .models import ReceptionNote, ReceptionItem
from .forms import ReceptionNoteForm, ReceptionItemFormSet
from apps.inventory.models import Product

class ReceptionNoteListView(LoginRequiredMixin, ListView):
    model = ReceptionNote
    template_name = 'reception_notes/reception_list.html'
    context_object_name = 'receptions'
    paginate_by = 15
    
    def get_queryset(self):
        return super().get_queryset().prefetch_related('items').order_by('-receipt_date')

class ReceptionNoteCreateView(LoginRequiredMixin, CreateView):
    model = ReceptionNote
    form_class = ReceptionNoteForm
    template_name = 'reception_notes/reception_form.html'
    success_url = reverse_lazy('reception_notes:list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ReceptionItemFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = ReceptionItemFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        with transaction.atomic():
            self.object = form.save()
            
            if formset.is_valid():
                formset.instance = self.object
                formset.save()
            else:
                return self.form_invalid(form)
            
        return redirect(self.get_success_url())

class ReceptionNoteDetailView(LoginRequiredMixin, DetailView):
    model = ReceptionNote
    template_name = 'reception_notes/reception_detail.html'
    context_object_name = 'reception'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.select_related('product')
        return context

class ReceptionNoteUpdateView(LoginRequiredMixin, UpdateView):
    model = ReceptionNote
    form_class = ReceptionNoteForm
    template_name = 'reception_notes/reception_form.html'
    success_url = reverse_lazy('reception_notes:list')
    
@transaction.atomic
def validate_reception_note(request, pk):
    reception_note = get_object_or_404(ReceptionNote, pk=pk)
    if request.method == 'POST' and reception_note.status == 'PENDING':
        # 1. Cambiar el estado de la nota a 'RECEIVED'
        reception_note.status = 'RECEIVED'
        reception_note.save()

        # 2. Iterar sobre cada item y actualizar el inventario
        for item in reception_note.items.all():
            item.product.current_stock = F('current_stock') + item.quantity
            item.product.save(update_fields=['current_stock'])

        return redirect('reception_notes:detail', pk=reception_note.pk)
    
    return redirect('reception_notes:detail', pk=reception_note.pk)