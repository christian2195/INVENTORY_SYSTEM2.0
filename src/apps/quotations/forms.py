from django import forms
from django.forms import inlineformset_factory
from .models import Quotation, QuotationItem
from apps.inventory.models import Product

class QuotationForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = ['client', 'quotation_number', 'total'] # 'date_created' eliminado
        # El widget para 'date_created' ya no es necesario aquí
        widgets = {
            'client': forms.TextInput(attrs={'class': 'form-control'}),
            'quotation_number': forms.TextInput(attrs={'class': 'form-control'}),
            'total': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }

class QuotationItemForm(forms.ModelForm):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), label="Producto")
    
    class Meta:
        model = QuotationItem
        fields = ['product', 'quantity', 'unit_price']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control'}),
        }

QuotationItemFormSet = inlineformset_factory(
    Quotation,
    QuotationItem,
    form=QuotationItemForm,
    extra=1,
    can_delete=True
)