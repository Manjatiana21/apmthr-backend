from rest_framework import serializers
from .models import MouvementStock
from catalogue.models import Produit
from commandes.models import Commande

class ProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produit
        fields = ['id', 'designation', 'prix', 'stock']

class CommandeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commande
        fields = ['id', 'client', 'statut', 'total', 'date_commande']

class MouvementStockSerializer(serializers.ModelSerializer):
    produit = ProduitSerializer(read_only=True)
    commande = CommandeSerializer(read_only=True)

    class Meta:
        model = MouvementStock
        fields = '__all__'
