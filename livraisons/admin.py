from django.contrib import admin
from .models import Livraison

@admin.register(Livraison)
class LivraisonAdmin(admin.ModelAdmin):
    list_display = ("get_commande", "get_client", "adresse", "statut", "date_prevue")
    list_filter = ("statut",)
    date_hierarchy = "date_prevue" 

    def get_commande(self, obj):
        return f"Commande #{obj.commande.id}"
    get_commande.short_description = "Commande"

    def get_client(self, obj):
        return obj.commande.client.username
    get_client.short_description = "Client"

    def adresse(self, obj):
        return obj.commande.adresse_livraison
    adresse.short_description = "Adresse de livraison"
