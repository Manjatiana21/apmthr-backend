from django import forms
from .models import Produit, TypeProduit, Fournisseur

class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['designation', 'description', 'stock', 'type_produit', 'fournisseur','prix','image']

class TypeProduitForm(forms.ModelForm):
    class Meta:
        model = TypeProduit
        fields = ['libelleTP']

class FournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = ['nom', 'contact', 'type_F']
