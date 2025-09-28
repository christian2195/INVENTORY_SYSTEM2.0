# src/apps/quotations/forms.py
from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from .models import Quotation, QuotationItem
from apps.inventory.models import Product

class QuotationForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = ['client', 'valid_until', 'notes']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select'}),
            'valid_until': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Establecer fecha de validez por defecto (30 días desde hoy)
        if not self.instance.pk and not self.data:
            from django.utils import timezone
            from datetime import timedelta
            default_date = timezone.now().date() + timedelta(days=30)
            self.fields['valid_until'].initial = default_date

class QuotationItemForm(forms.ModelForm):
    class Meta:
        model = QuotationItem
        fields = ['product', 'quantity', 'unit_price']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'form-select product-select',
                'data-live-search': 'true'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control quantity-input',
                'min': '1',
                'step': '1'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-control price-input',
                'min': '0',
                'step': '0.01'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ordenar productos por descripción
        self.fields['product'].queryset = Product.objects.all().order_by('description')
        
        # CORREGIDO: Cambiar 'code' por 'product_code'
        self.fields['product'].label_from_instance = lambda obj: f"{obj.product_code} - {obj.description}"
    
    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity')
        unit_price = cleaned_data.get('unit_price')
        
        # Solo validar si hay datos (no validar forms vacíos)
        if any([product, quantity, unit_price]):
            if not product:
                raise ValidationError({'product': 'Debe seleccionar un producto'})
            if not quantity or quantity <= 0:
                raise ValidationError({'quantity': 'La cantidad debe ser mayor a 0'})
            if unit_price is None or unit_price < 0:
                raise ValidationError({'unit_price': 'El precio unitario no puede ser negativo'})
        
        return cleaned_data

QuotationItemFormSet = inlineformset_factory(
    Quotation,
    QuotationItem,
    form=QuotationItemForm,
    extra=1,
    can_delete=True,
    can_delete_extra=True
)