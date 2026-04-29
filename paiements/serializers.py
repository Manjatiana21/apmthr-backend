from rest_framework import serializers
from .models import ModePaiement, Paiement
from commandes.models import Commande, Details 
from comptes.models import Utilisateur
from factures.serializers import FactureSerializer


class ModePaiementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModePaiement
        fields = '__all__'

class UtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = ['id', 'username', 'email', 'role']

class DetailCommandeSerializer(serializers.ModelSerializer):
    produit = serializers.CharField(source="produit.designation", read_only=True)

    class Meta:
        model = Details   
        fields = ["id", "produit", "quantite", "prix_unitaire", "sous_total"]

class CommandeSerializer(serializers.ModelSerializer):
    details = DetailCommandeSerializer(many=True, read_only=True)

    class Meta:
        model = Commande
        fields = ["id", "details", "statut", "total"]

class PaiementSerializer(serializers.ModelSerializer):
    client = serializers.CharField(source="client.username", read_only=True)
    commande = CommandeSerializer(read_only=True)
    mode_paiement = serializers.CharField(source="mode_paiement.mode_paiement", read_only=True)
    facture = FactureSerializer(source="commande.facture", read_only=True) 
    class Meta:
        model = Paiement
        fields = [
            "id",
            "client",
            "commande",
            "montant",
            "mode_paiement",
            "statut",
            "date_paiement",
            "facture"
        ]
