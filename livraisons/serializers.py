from rest_framework import serializers
from .models import Livraison
from commandes.serializers import CommandeSerializer

class LivraisonSerializer(serializers.ModelSerializer):
    commande = CommandeSerializer(read_only=True)
    client = serializers.CharField(source="commande.client.username", read_only=True)
    adresse = serializers.CharField(source="commande.adresse_livraison", read_only=True)
    produit_designation = serializers.SerializerMethodField()

    class Meta:
        model = Livraison
        fields = ["id", "statut", "date_prevue", "client", "adresse", "produit_designation", "commande"]


    def get_produit_designation(self, obj):
        details = obj.commande.details.all()
        if details.exists():
            return details.first().produit.designation
        return None
