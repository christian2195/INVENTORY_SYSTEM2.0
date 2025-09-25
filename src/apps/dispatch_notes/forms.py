# src/apps/dispatch_notes/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import DispatchNote, DispatchItem
from apps.inventory.models import Product

class DispatchNoteForm(forms.ModelForm):
    class Meta:
        model = DispatchNote
        fields = [
            #'dispatch_number', 
            'client', 
            'beneficiary',
            'supplier',
            'order_number',
            'driver_name',
            'driver_id',
            'vehicle_type',
            'vehicle_color',
            'license_plate',
            'notes'
        ]
        widgets = {
            'dispatch_number': forms.TextInput(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'beneficiary': forms.TextInput(attrs={'class': 'form-control'}),
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'order_number': forms.TextInput(attrs={'class': 'form-control'}),
            'driver_name': forms.TextInput(attrs={'class': 'form-control'}),
            'driver_id': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle_type': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle_color': forms.TextInput(attrs={'class': 'form-control'}),
            'license_plate': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class DispatchItemForm(forms.ModelForm):
    # Campo para la búsqueda que no está en el modelo
    product_search = forms.CharField(
        label='Buscar Producto',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control product-search', 
            'placeholder': 'Buscar por código o descripción...'
        })
    )
    
    product_description = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
            'placeholder': 'Descripción del producto...'
        }),
        label="Descripción"
    )
    
    class Meta:
        model = DispatchItem
        fields = ['product', 'quantity', 'unit_price', 'brand', 'model']
        widgets = {
            'product': forms.HiddenInput(), # Campo oculto para guardar el ID
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer que los campos sean requeridos
        self.fields['product'].required = True
        self.fields['quantity'].required = True
        self.fields['unit_price'].required = True
        
        # Si el formulario ya tiene una instancia, cargamos el valor del campo de búsqueda
        if self.instance and self.instance.pk and self.instance.product:
            self.fields['product_search'].initial = self.instance.product.product_code
            self.fields['product_description'].initial = self.instance.product.description
    
    def clean(self):  # FIXED: This method should be at the same level as __init__
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        product_search = cleaned_data.get('product_search')
        
        print(f"=== CLEAN DEBUG ===")
        print(f"Product: {product}")
        print(f"Product search: {product_search}")
        
        # Validar que el producto sea requerido
        if not product:
            self.add_error('product', 'Este campo es requerido')
            self.add_error('product_search', 'Debe seleccionar un producto')
            print("❌ Product field is required")
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Si tenemos un producto pero no precio unitario, usar el precio del producto
        if instance.product and not instance.unit_price:
            instance.unit_price = instance.product.unit_price
        
        if commit:
            instance.save()
        
        return instance
            
DispatchItemFormSet = inlineformset_factory(
    DispatchNote,
    DispatchItem,
    form=DispatchItemForm,
    extra=1,
    can_delete=True,
   # fields=['product', 'quantity', 'unit_price', 'brand', 'model', 'product_search', 'product_description']
    max_num=500,
    validate_max=False,  # No validar máximo si hay forms vacíos
    exclude=[]  # Asegurar que no excluya campos necesarios
)