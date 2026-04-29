from django.urls import path
from . import views, views_api

urlpatterns = [
    path("ajouter-produit/", views.ajouter_produit, name="ajouter_produit"),
    path("<int:id>/", views.detail_produit, name="detail_produit"),  # detail_produit.html
    path("", views.liste_produits, name="liste_produits"),  # liste_produits.html
    path("type/<str:type>/", views.produits_par_type, name="liste_produit_par_type"),  # liste_produit_par_type.html

    path("produits/<int:id>/modifier/", views.modifier_produit, name="modifier_produit"), 
    path("produits/<int:id>/supprimer/", views.supprimer_produit, name="supprimer_produit"),
    path("produits/", views.liste_des_produits, name="listes_des_produits"),

    path("api/produits/list/", views_api.api_liste_produits, name="api_liste_produits"),
    path("api/produits/<int:id>/detail/", views_api.api_detail_produit, name="api_detail_produit"),
    path("api/produits/<int:id>/modifier/", views_api.api_modifier_produit, name="api_modifier_produit"),
    path("api/produits/<int:id>/supprimer/", views_api.api_supprimer_produit, name="api_supprimer_produit"),
    path("api/produits/ajouter/", views_api.api_ajouter_produit, name="api_ajouter_produit"),
    path("api/produits/type/<int:type_id>/", views_api.api_produits_par_type, name="api_produits_par_type"),
    path("api/types-produits/", views_api.types_produits_list, name="types_produits_list"),
    path("api/fournisseurs/", views_api.fournisseurs_list, name="fournisseurs_list"),

]
