from rest_framework import serializers
from .models import Produit, TypeProduit, Fournisseur
from django.utils import timezone

class TypeProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeProduit
        fields = '__all__'

class FournisseurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fournisseur
        fields = '__all__'

class ProduitSerializer(serializers.ModelSerializer):
    type_produit = TypeProduitSerializer(read_only=True)
    type_produit_id = serializers.PrimaryKeyRelatedField(
        queryset=TypeProduit.objects.all(), write_only=True, source="type_produit"
    )

    fournisseur = FournisseurSerializer(read_only=True)
    fournisseur_id = serializers.PrimaryKeyRelatedField(
        queryset=Fournisseur.objects.all(), write_only=True, source="fournisseur"
    )

    # ✅ Champ calculé
    date_ajout_formatee = serializers.SerializerMethodField()

    def get_date_ajout_formatee(self, obj):
        return timezone.localtime(obj.date_ajout).strftime("%d/%m/%Y")

    class Meta:
        model = Produit
        fields = [
            "id",
            "designation",
            "description",
            "stock",
            "type_produit",
            "type_produit_id",
            "fournisseur",
            "fournisseur_id",
            "prix",
            "image",
            "date_ajout",
            "is_active",
            "date_ajout_formatee",  # ✅ champ calculé
        ]
        extra_kwargs = {
            "is_active": {"default": True}
        }
