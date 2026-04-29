from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur

class UtilisateurAdmin(UserAdmin):
    # ✅ Colonnes affichées dans la liste
    list_display = (
        "username", "email", "adresse", "role", "privilege",
        "is_active", "suspension_reason", "is_staff", "is_superuser"
    )

    # ✅ Filtres latéraux
    list_filter = ("role", "privilege", "is_active", "is_staff", "is_superuser")

    # ✅ Barre de recherche
    search_fields = ("username", "email", "adresse")

    # ✅ Champs affichés dans le formulaire de modification
    fieldsets = UserAdmin.fieldsets + (
        ("Informations supplémentaires", {
            "fields": ("adresse", "role", "privilege", "suspension_reason")
        }),
    )

    # ✅ Champs affichés dans le formulaire d’ajout
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Informations supplémentaires", {
            "fields": ("adresse", "role", "privilege")
        }),
    )

    # ✅ Actions personnalisées
    actions = ["suspendre_utilisateurs", "reactiver_utilisateurs"]

    def suspendre_utilisateurs(self, request, queryset):
        """Suspendre plusieurs utilisateurs en un clic."""
        queryset.update(is_active=False, suspension_reason="Suspendu par admin")
        self.message_user(request, "Les comptes sélectionnés ont été suspendus.")

    suspendre_utilisateurs.short_description = "Suspendre les utilisateurs sélectionnés"

    def reactiver_utilisateurs(self, request, queryset):
        """Réactiver plusieurs utilisateurs en un clic."""
        queryset.update(is_active=True, suspension_reason=None)
        self.message_user(request, "Les comptes sélectionnés ont été réactivés.")

    reactiver_utilisateurs.short_description = "Réactiver les utilisateurs sélectionnés"


# ✅ Enregistrement du modèle dans l’admin
admin.site.register(Utilisateur, UtilisateurAdmin)
