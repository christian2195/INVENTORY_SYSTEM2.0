# src/apps/returns/forms.py
from django import forms
from django.forms import inlineformset_factory

# Importar los modelos explícitamente
from .models import ReturnNote, ReturnItem

class ReturnNoteForm(forms.ModelForm):
    class Meta:
        model = ReturnNote
        fields = ['dispatch_note', 'client', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'dispatch_note': forms.Select(attrs={'class': 'form-select'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].required = False
        self.fields['dispatch_note'].required = False

class ReturnItemForm(forms.ModelForm):
    class Meta:
        model = ReturnItem
        fields = ['product', 'quantity']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

# Crear el formset
ReturnItemFormSet = inlineformset_factory(
    ReturnNote,
    ReturnItem,
    form=ReturnItemForm,
    extra=1,
    can_delete=True
)