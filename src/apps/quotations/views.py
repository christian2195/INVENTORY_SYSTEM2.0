# src/apps/quotations/views.py
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from .models import Quotation, QuotationItem
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

class QuotationListView(LoginRequiredMixin, ListView):
    model = Quotation
    template_name = 'quotations/quotation_list.html'
    context_object_name = 'quotations'

class QuotationDetailView(LoginRequiredMixin, DetailView):
    model = Quotation
    template_name = 'quotations/quotation_detail.html'
    context_object_name = 'quotation'

class QuotationCreateView(LoginRequiredMixin, CreateView):
    model = Quotation
    fields = ['quotation_number', 'client', 'total', 'is_approved']
    template_name = 'quotations/quotation_form.html'
    success_url = reverse_lazy('quotations:list')

class QuotationUpdateView(LoginRequiredMixin, UpdateView):
    model = Quotation
    fields = ['quotation_number', 'client', 'total', 'is_approved']
    template_name = 'quotations/quotation_form.html'
    success_url = reverse_lazy('quotations:list')