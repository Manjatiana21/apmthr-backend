from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.db.models import Sum
from .models import MouvementStock

@admin.register(MouvementStock)
class MouvementStockAdmin(admin.ModelAdmin):
    list_display = ('produit', 'quantite', 'type_mouvement', 'date_mouvement')
    list_filter = ('type_mouvement', 'date_mouvement')
    search_fields = ('produit__designation', 'type_mouvement')

   
    def get_urls(self):
        urls = super().get_urls()  
        custom_urls = [
            path("rapport-mouvement/", self.admin_site.admin_view(self.rapport_mouvements), name="rapport_mouvements"),
        ]
        return custom_urls + urls

    def rapport_mouvements(self, request):
        mouvements = MouvementStock.objects.values("type_mouvement", "date_mouvement__month").annotate(
            total=Sum("quantite")
        )
        data = {}
        for m in mouvements:
            mois = m["date_mouvement_month"]
            type_mvt = m["type_mouvement"]
            if mois not in data:
                data[mois] = {"ENTREE": 0, "SORTIE": 0}
            data[mois][type_mvt] = m["total"]

        mouvements_list = MouvementStock.objects.all().order_by("-date_mouvement")

        return render(request, "rapport_mouvements.html", {"data": data, "mouvements": mouvements_list})
