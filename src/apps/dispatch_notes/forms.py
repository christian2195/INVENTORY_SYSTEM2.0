# src/apps/dispatch_notes/forms.py
from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from .models import DispatchNote, DispatchItem
from apps.inventory.models import Product

class DispatchNoteForm(forms.ModelForm):
    class Meta:
        model = DispatchNote
        fields = [
            'dispatch_number', 
            'client', 
            'beneficiary',
            'supplier',
            'order_number',
            'dispatch_date',
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
            'dispatch_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
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
    
    # NUEVO: Campo para mostrar stock disponible
    current_stock = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control stock-display',
            'readonly': 'readonly',
            'placeholder': 'Stock disponible...'
        }),
        label="Stock Disponible"
    )
    
    class Meta:
        model = DispatchItem
        fields = ['product', 'quantity', 'unit_price', 'brand', 'model']
        widgets = {
            'product': forms.HiddenInput(), # Campo oculto para guardar el ID
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
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer que los campos sean requeridos
        self.fields['product'].required = True
        self.fields['quantity'].required = True
        self.fields['unit_price'].required = True
        
        # Si el formulario ya tiene una instancia, cargamos los valores
        if self.instance and self.instance.pk and self.instance.product:
            self.fields['product_search'].initial = self.instance.product.product_code
            self.fields['product_description'].initial = self.instance.product.description
            # NUEVO: Mostrar stock disponible
            if hasattr(self.instance.product, 'current_stock'):
                stock = self.instance.product.current_stock
                self.fields['current_stock'].initial = f"{stock} unidades"
                
                # Marcar como requerido si hay stock insuficiente (solo para visualización)
                if stock <= 0:
                    self.fields['current_stock'].widget.attrs['class'] += ' text-danger'
    
    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity')
        unit_price = cleaned_data.get('unit_price')
        
        print(f"=== CLEAN DEBUG ===")
        print(f"Product: {product}")
        print(f"Quantity: {quantity}")
        print(f"Unit Price: {unit_price}")
        
        # Validar que el producto sea requerido
        if not product:
            self.add_error('product', 'Este campo es requerido')
            self.add_error('product_search', 'Debe seleccionar un producto')
            print("❌ Product field is required")
        
        # Validar cantidad
        if quantity is not None:
            if quantity <= 0:
                self.add_error('quantity', 'La cantidad debe ser mayor a 0')
                print("❌ Quantity must be greater than 0")
        
        # Validar precio unitario
        if unit_price is not None and unit_price < 0:
            self.add_error('unit_price', 'El precio unitario no puede ser negativo')
            print("❌ Unit price cannot be negative")
        
        # NUEVA VALIDACIÓN: Verificar stock disponible
        if product and quantity:
            if hasattr(product, 'current_stock'):
                current_stock = product.current_stock
                if current_stock < quantity:
                    error_msg = f'Stock insuficiente. Disponible: {current_stock}, Solicitado: {quantity}'
                    self.add_error('quantity', error_msg)
                    self.add_error('product_search', error_msg)  # También mostrar en búsqueda
                    print(f"❌ Stock insuficiente: {current_stock} < {quantity}")
                
                # Advertencia si el stock es bajo (menos del 10%)
                elif current_stock > 0 and quantity > current_stock * 0.9:
                    print(f"⚠️ Stock bajo: {current_stock} unidades disponibles")
            
            # Advertencia si el producto no tiene stock definido
            elif not hasattr(product, 'current_stock'):
                print(f"⚠️ Producto sin información de stock: {product}")
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Si tenemos un producto pero no precio unitario, usar el precio del producto
        if instance.product and not instance.unit_price:
            if hasattr(instance.product, 'unit_price') and instance.product.unit_price:
                instance.unit_price = instance.product.unit_price
                print(f"💰 Precio unitario asignado desde producto: {instance.unit_price}")
            else:
                instance.unit_price = 0
                print("⚠️ Precio unitario establecido a 0 (no disponible en producto)")
        
        # Calcular subtotal automáticamente
        if instance.quantity and instance.unit_price:
            instance.subtotal = instance.quantity * instance.unit_price
            print(f"🧮 Subtotal calculado: {instance.subtotal}")
        
        if commit:
            instance.save()
            print(f"✅ Item guardado: {instance.product} x {instance.quantity}")
        
        return instance

DispatchItemFormSet = inlineformset_factory(
    DispatchNote,
    DispatchItem,
    form=DispatchItemForm,
    extra=1,
    can_delete=True,
    max_num=500,
    validate_max=False,
    exclude=[]
)