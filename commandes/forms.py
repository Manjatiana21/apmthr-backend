from django import forms
from .models import Commande, Details
from paiements.models import ModePaiement

class CommandeCompleteForm(forms.ModelForm):
    mode_paiement = forms.ModelChoiceField(queryset=ModePaiement.objects.all())
    adresse_livraison = forms.CharField(max_length=255)
    date_livraison = forms.DateField(widget=forms.SelectDateWidget)

    class Meta:
        model = Commande
        fields = ['quantite', 'adresse_livraison', 'date_livraison', 'mode_paiement']