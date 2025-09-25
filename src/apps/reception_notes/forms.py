# src/apps/reception_notes/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import ReceptionNote, ReceptionItem

class ReceptionNoteForm(forms.ModelForm):
    class Meta:
        model = ReceptionNote
        fields = ['receipt_number', 'supplier', 'notes']

class ReceptionItemForm(forms.ModelForm):
    class Meta:
        model = ReceptionItem
        fields = ['product', 'quantity', 'unit_price']

ReceptionItemFormSet = inlineformset_factory(
    ReceptionNote,
    ReceptionItem,
    form=ReceptionItemForm,
    extra=1,
    can_delete=True
)