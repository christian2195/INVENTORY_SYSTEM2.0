# src/apps/returns/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db import transaction
from django.db.models import F
from .models import ReturnNote, ReturnItem
from .forms import ReturnNoteForm, ReturnItemFormSet
from apps.inventory.models import Product

class ReturnNoteListView(LoginRequiredMixin, ListView):
    model = ReturnNote
    template_name = 'returns/return_list.html'
    context_object_name = 'returns'
    paginate_by = 15

class ReturnNoteCreateView(LoginRequiredMixin, CreateView):
    model = ReturnNote
    form_class = ReturnNoteForm
    template_name = 'returns/return_form.html'
    success_url = reverse_lazy('returns:list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ReturnItemFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = ReturnItemFormSet(instance=self.object)
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

class ReturnNoteDetailView(LoginRequiredMixin, DetailView):
    model = ReturnNote
    template_name = 'returns/return_detail.html'
    context_object_name = 'return_note'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.select_related('product')
        return context

@transaction.atomic
def process_return_note(request, pk):
    return_note = get_object_or_404(ReturnNote, pk=pk)
    if request.method == 'POST' and return_note.status == 'PENDING':
        # 1. Cambiar el estado de la nota a 'RETURNED'
        return_note.status = 'RETURNED'
        return_note.save()

        # 2. Iterar sobre cada item y sumar al inventario
        for item in return_note.items.all():
            item.product.current_stock = F('current_stock') + item.quantity
            item.product.save(update_fields=['current_stock'])

        return redirect('returns:detail', pk=return_note.pk)
    
    return redirect('returns:detail', pk=return_note.pk)