# src/apps/reception_notes/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import ReceptionNote, ReceptionItem

class ReceptionNoteForm(forms.ModelForm):
    class Meta:
        model = ReceptionNote
        fields = ['supplier', 'notes']  # Removido 'receipt_number'
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Observaciones opcionales...'}),
        }

class ReceptionItemForm(forms.ModelForm):
    class Meta:
        model = ReceptionItem
        fields = ['product', 'quantity', 'unit_price']
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': 1, 'step': 1}),
            'unit_price': forms.NumberInput(attrs={'min': 0, 'step': '0.01'}),
        }

ReceptionItemFormSet = inlineformset_factory(
    ReceptionNote,
    ReceptionItem,
    form=ReceptionItemForm,
    extra=1,
    can_delete=True
)