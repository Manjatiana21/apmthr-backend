from django import forms
from .models import Paiement, ModePaiement

class ModePaimentForm(forms.ModelForm):
    class Meta:
        model = ModePaiement
        fields = ['mode_paiement', 'numero_assoc']

        