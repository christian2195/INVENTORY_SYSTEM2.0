from django import forms
from django.core.exceptions import ValidationError
from .models import Movement

class MovementForm(forms.ModelForm):
    class Meta:
        model = Movement
        fields = ['product', 'movement_type', 'quantity', 'unit_price', 'observations']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'movement_type': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'observations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        movement_type = cleaned_data.get('movement_type')
        quantity = cleaned_data.get('quantity')
        product = cleaned_data.get('product')
        
        if movement_type == 'OUT' and product and quantity:
            if quantity > product.current_stock:
                raise ValidationError(
                    f"No hay suficiente stock de {product.description}. "
                    f"Stock disponible: {product.current_stock}, "
                    f"Intenta sacar: {quantity}"
                )
        return cleaned_data
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity and quantity <= 0:
            raise ValidationError("La cantidad debe ser mayor a cero.")
        return quantity
    
    def clean_unit_price(self):
        unit_price = self.cleaned_data.get('unit_price')
        if unit_price and unit_price < 0:
            raise ValidationError("El precio unitario no puede ser negativo.")
        return unit_price