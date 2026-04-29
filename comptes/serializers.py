from rest_framework import serializers
from .models import Utilisateur, Notification
from paiements.models import Paiement
import re

# =========================
# 🔹 Utilisateur
# =========================
class UtilisateurSerializer(serializers.ModelSerializer):
    """Serializer standard pour afficher les infos utilisateur (sans mot de passe)."""
    class Meta:
        model = Utilisateur
        fields = [
            'id', 'username', 'email', 'adresse', 'telephone',
            'role', 'privilege', 'is_active', 'suspension_reason', 'date_joined'
        ]


# =========================
# 🔹 Admin : gestion suspension / réactivation
# =========================
class AdminUtilisateurSerializer(serializers.ModelSerializer):
    """Serializer pour l’Admin afin de gérer le statut des comptes."""
    class Meta:
        model = Utilisateur
        fields = [
            'id', 'username', 'email', 'adresse',
            'role', 'privilege', 'is_active', 'suspension_reason', 'date_joined'
        ]
        read_only_fields = ['username', 'email', 'adresse', 'role', 'privilege', 'date_joined']


class SuspensionSerializer(serializers.Serializer):
    """Serializer pour suspendre un compte avec une raison."""
    reason = serializers.CharField(required=False, allow_blank=True)

    def update(self, instance, validated_data):
        instance.is_active = False
        instance.suspension_reason = validated_data.get("reason", "Suspension par admin")
        instance.save()
        return instance


class ReactivationSerializer(serializers.Serializer):
    """Serializer pour réactiver un compte suspendu."""
    def update(self, instance, validated_data):
        instance.is_active = True
        instance.suspension_reason = None
        instance.save()
        return instance


# =========================
# 🔹 Notifications
# =========================
class NotificationSerializer(serializers.ModelSerializer):
    utilisateur = UtilisateurSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ["id", "message", "lu", "date_creation", "utilisateur"]


# =========================
# 🔹 Paiements
# =========================
class PaiementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paiement
        fields = "__all__"


# =========================
# 🔹 Inscription (client)
# =========================
class InscriptionSerializer(serializers.ModelSerializer):
    """Serializer pour inscription avec validation du mot de passe."""
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = Utilisateur
        fields = ["username", "email", "adresse", "telephone", "password1", "password2"]

    def validate_password1(self, value):
        # ✅ Vérification de la complexité du mot de passe
        if len(value) < 8:
            raise serializers.ValidationError("Le mot de passe doit contenir au moins 8 caractères.")
        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError("Le mot de passe doit contenir au moins une majuscule.")
        if not re.search(r"[a-z]", value):
            raise serializers.ValidationError("Le mot de passe doit contenir au moins une minuscule.")
        if not re.search(r"[0-9]", value):
            raise serializers.ValidationError("Le mot de passe doit contenir au moins un chiffre.")
        if not re.search(r"[@$!%*?&]", value):
            raise serializers.ValidationError("Le mot de passe doit contenir au moins un caractère spécial (@$!%*?&).")
        return value

    def validate(self, data):
        # ✅ Vérification que les deux mots de passe correspondent
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return data

    def create(self, validated_data):
        user = Utilisateur(
            username=validated_data["username"],
            email=validated_data.get("email"),
            adresse=validated_data.get("adresse"),
            role="CLIENT" ,
            telephone=validated_data.get('telephone')
        )
        user.set_password(validated_data["password1"])
        user.save()
        return user

class ModifierProfilSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Utilisateur
        fields = ["username", "email", "adresse", "telephone", "old_password", "new_password"]

    def update(self, instance, validated_data):
        old_password = validated_data.pop("old_password", None)
        new_password = validated_data.pop("new_password", None)

        # Vérifier ancien mot de passe avant modification
        if old_password and new_password:
            if not instance.check_password(old_password):
                raise serializers.ValidationError({"old_password": "Ancien mot de passe incorrect"})
            instance.set_password(new_password)

        return super().update(instance, validated_data)
