from rest_framework import serializers
from .models import Commande, Details, CommandeItem
from comptes.models import Utilisateur
from catalogue.models import Produit
from paiements.models import Paiement

# =========================
# Utilisateur
# =========================
class UtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = ['id', 'username', 'email', 'role']

# =========================
# Produit
# =========================
class ProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produit
        fields = ['id', 'designation', 'prix', 'stock']

# =========================
# Détails de commande
# =========================
class DetailsSerializer(serializers.ModelSerializer):
    produit = ProduitSerializer(read_only=True)
    produit_id = serializers.PrimaryKeyRelatedField(
        queryset=Produit.objects.all(), source="produit", write_only=True
    )

    class Meta:
        model = Details
        fields = ["id", "produit", "produit_id", "quantite", "prix_unitaire", "sous_total"]
        read_only_fields = ["id", "produit", "prix_unitaire", "sous_total"]


# =========================
# CommandeItem (si utilisé)
# =========================
class CommandeItemSerializer(serializers.ModelSerializer):
    produit = ProduitSerializer(read_only=True)

    class Meta:
        model = CommandeItem
        fields = ["id", "produit", "quantite"]

# =========================
# Paiement lié à une commande
# =========================
class PaiementSerializer(serializers.ModelSerializer):
    mode_paiement = serializers.CharField(source="mode_paiement.mode_paiement", read_only=True)

    class Meta:
        model = Paiement
        fields = ['id', 'mode_paiement', 'montant', 'date_paiement', 'statut']

# =========================
# Commande principale
# =========================
class CommandeSerializer(serializers.ModelSerializer):
    client = UtilisateurSerializer(read_only=True)
    details = DetailsSerializer(many=True, read_only=True)
    paiements = PaiementSerializer(many=True, read_only=True)  # ✅ correction

    class Meta:
        model = Commande
        fields = [
            "id",
            "client",
            "details",
            "total",
            "statut",
            "date_commande",
            "paiements",
            "adresse_livraison",
            "mode_paiement",
        ]
        read_only_fields = [
            "id",
            "client",
            "date_commande",
            "total",
            "statut",
            "details",
            "paiements",
        ]

class PanierSerializer(serializers.ModelSerializer):
    produits = DetailsSerializer(many=True, write_only=True, required=False)
    client = UtilisateurSerializer(read_only=True)

    class Meta:
        model = Commande
        fields = [
            "id",
            "client",
            "adresse_livraison",
            "mode_paiement",
            "produit",      # ✅ pour commande simple
            "quantite",     # ✅ pour commande simple
            "produits"      # ✅ pour panier multi-produits
        ]
        read_only_fields = ["id", "client"]

    def create(self, validated_data):
        produits_data = validated_data.pop("produits", [])
        client = self.context["request"].user
        commande = Commande.objects.create(client=client, **validated_data)

        # ✅ Cas commande simple
        if commande.produit and commande.quantite:
            Details.objects.create(
                commande=commande,
                produit=commande.produit,
                quantite=commande.quantite,
                prix_unitaire=commande.produit.prix,
                sous_total=commande.quantite * commande.produit.prix,
            )

        # ✅ Cas panier multi-produits
        for produit_data in produits_data:
            produit = produit_data["produit"]  # mappé depuis produit_id
            quantite = produit_data["quantite"]
            prix_unitaire = produit.prix
            Details.objects.create(
                commande=commande,
                produit=produit,
                quantite=quantite,
                prix_unitaire=prix_unitaire,
                sous_total=quantite * prix_unitaire,
            )

        commande.calculerTotal()
        return commande
