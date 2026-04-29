from django.contrib import admin
from .models import ModePaiement, Paiement

@admin.register(ModePaiement)
class ModePaiementAdmin(admin.ModelAdmin):
    list_display = ("id", "mode_paiement")  
    search_fields = ("mode_paiement",)

@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ("id", "commande", "mode_paiement", "montant", "statut")
    list_filter = ("mode_paiement", "statut")
    search_fields = ("commande__id", "mode_paiement__mode_paiement")
