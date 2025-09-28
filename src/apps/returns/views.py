# src/apps/returns/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db import transaction
from django.db.models import F
from django.contrib import messages
from django import forms
from .models import ReturnNote, ReturnItem
from .forms import ReturnNoteForm, ReturnItemFormSet
from apps.dispatch_notes.models import DispatchNote

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
    
    def get_form(self, form_class=None):
        """Obtener el formulario con campos ocultos configurados"""
        form = super().get_form(form_class)
        # Configurar campos que no deben mostrarse al usuario
        form.fields['status'] = forms.CharField(
            initial='PENDING',
            widget=forms.HiddenInput()
        )
        form.fields['created_by'] = forms.CharField(
            initial=self.request.user.id,
            widget=forms.HiddenInput()
        )
        form.fields['return_date'] = forms.CharField(
            widget=forms.HiddenInput()
        )
        return form
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ReturnItemFormSet(self.request.POST)
        else:
            context['formset'] = ReturnItemFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        with transaction.atomic():
            # Guardar el formulario principal
            self.object = form.save(commit=False)
            self.object.created_by = self.request.user
            
            # Si hay un dispatch_note, establecer el cliente automáticamente
            if self.object.dispatch_note and not self.object.client:
                self.object.client = self.object.dispatch_note.client
            
            # Guardar para generar el número automático
            self.object.save()
            
            # Guardar el formset
            if formset.is_valid():
                formset.instance = self.object
                formset.save()
            else:
                # Si el formset no es válido, mostrar errores
                return self.form_invalid(form)
            
        messages.success(self.request, f'Nota de devolución #{self.object.return_number} creada exitosamente.')
        return redirect(self.get_success_url())

class ReturnNoteCreateFromDispatchView(LoginRequiredMixin, CreateView):
    model = ReturnNote
    form_class = ReturnNoteForm
    template_name = 'returns/return_form.html'
    success_url = reverse_lazy('returns:list')
    
    def get_initial(self):
        initial = super().get_initial()
        dispatch_note_id = self.kwargs.get('dispatch_id')
        if dispatch_note_id:
            dispatch_note = get_object_or_404(DispatchNote, id=dispatch_note_id)
            initial['dispatch_note'] = dispatch_note
            initial['client'] = dispatch_note.client
        return initial
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Configurar campos ocultos
        form.fields['status'] = forms.CharField(
            initial='PENDING',
            widget=forms.HiddenInput()
        )
        form.fields['created_by'] = forms.CharField(
            initial=self.request.user.id,
            widget=forms.HiddenInput()
        )
        form.fields['return_date'] = forms.CharField(
            widget=forms.HiddenInput()
        )
        return form
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ReturnItemFormSet(self.request.POST)
        else:
            context['formset'] = ReturnItemFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.created_by = self.request.user
            
            if self.object.dispatch_note and not self.object.client:
                self.object.client = self.object.dispatch_note.client
            
            self.object.save()
            
            if formset.is_valid():
                formset.instance = self.object
                formset.save()
            else:
                return self.form_invalid(form)
            
        messages.success(self.request, f'Nota de devolución #{self.object.return_number} creada exitosamente.')
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
        return_note.status = 'RETURNED'
        return_note.save()

        for item in return_note.items.all():
            item.product.current_stock = F('current_stock') + item.quantity
            item.product.save(update_fields=['current_stock'])

        messages.success(request, f'Nota de devolución #{return_note.return_number} procesada exitosamente.')
        return redirect('returns:detail', pk=return_note.pk)
    
    return redirect('returns:detail', pk=return_note.pk)
