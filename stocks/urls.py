from django.urls import path
from rest_framework.routers import DefaultRouter
from .views_api import MouvementStockViewSet, rapport_mouvement
from . import views, views_api

router = DefaultRouter()
router.register(r"mouvements", MouvementStockViewSet, basename="mouvementstock")

urlpatterns = [
    # API spécifique
    path("rapport/", rapport_mouvement, name="rapport_mouvement"),

    # Vues classiques
    path("ajouter-mouvement/", views.ajouter_mouvement, name="ajouter_mouvement"),
    path("gestion/", views.gestion_stock, name="gestion_stock"),
    path("historique-stock/<int:produit_id>/", views.historique_stock, name="historique_stock"),
    path("rapport-html/", views.rapport_mouvements, name="rapport_mouvement_html"),


    path("api/stocks/", views_api.api_gestion_stock, name="api_gestion_stock"),
    path("api/stocks/ajouter/", views_api.api_ajouter_mouvement, name="api_ajouter_mouvement"),
    path("api/stocks/historique/<int:produit_id>/", views_api.api_historique_stock, name="api_historique_stock"),
    path("api/stocks/rapport/", views_api.api_rapport_mouvements, name="api_rapport_mouvements"),

]

urlpatterns += router.urls
