# src/apps/orders/forms.py
from django import forms
from .models import Order, OrderItem
from django.forms import inlineformset_factory
from apps.inventory.models import Product

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['client', 'supplier', 'delivery_date', 'notes']
        widgets = {
            'client': forms.Select(attrs={
                'class': 'form-select',
                'data-placeholder': 'Seleccionar cliente...'
            }),
            'supplier': forms.Select(attrs={
                'class': 'form-select',
                'data-placeholder': 'Seleccionar proveedor...'
            }),
            'delivery_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales...'
            }),
        }
        labels = {
            'delivery_date': 'Fecha de Entrega Esperada',
            'notes': 'Observaciones'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ordenar clientes y proveedores alfabéticamente
        self.fields['client'].queryset = self.fields['client'].queryset.order_by('name')
        self.fields['supplier'].queryset = self.fields['supplier'].queryset.order_by('name')

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'unit_price']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'form-select product-select',
                'data-placeholder': 'Seleccionar producto...'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control quantity-input',
                'min': '1',
                'step': '1'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-control price-input',
                'min': '0.01',
                'step': '0.01',
                'placeholder': '0.00'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ordenar productos por descripción (que parece ser el nombre)
        self.fields['product'].queryset = Product.objects.all().order_by('description')

# Formset mejorado con validación
OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
    max_num=20
)