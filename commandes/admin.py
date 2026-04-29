from django.contrib import admin
from .models import Commande, Details
from comptes.models import Notification  # ✅ attention : Notification est dans comptes.models

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "total", "statut", "date_commande", "mode_paiement", "adresse_livraison")
    list_filter = ("statut", "date_commande", "mode_paiement")
    search_fields = ("client__username", "adresse_livraison")

@admin.register(Details)
class DetailsAdmin(admin.ModelAdmin):
    list_display = ("id", "commande", "produit", "quantite", "prix_unitaire", "sous_total")
    search_fields = ("commande__id", "produit__designation")

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("utilisateur", "message", "lu", "date_creation")
    list_filter = ("lu", "date_creation")
