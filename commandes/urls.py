from django.urls import path
from . import views, views_api

urlpatterns = [
    # --- VUES HTML (côté client) ---
    path("mes/", views.client_commande, name="client_commandes"),
    path("consulter/<int:id>/", views.consulter_commande, name="consulter_commande"),
    path("passer/<int:produit_id>/", views.passer_commande, name="passer_commande"),
    path("mes-commandes-annulees/", views.commandes_annulees, name="commandes_annulees"),

    # --- VUES HTML (côté admin métier) ---
    path("admin/commandes/", views.gestion_commandes, name="gestion_commandes"),
    path("admin/commandes/<int:id>/", views.detail_commande_admin, name="detail_commande_admin"),
    path("admin/commandes/<int:id>/valider/", views.valider_commande, name="valider_commande"),
    path("admin/commandes/<int:id>/annuler/", views.annuler_commande, name="annuler_commande"),
    path("commandes/<int:id>/delete/", views.supprimer_commande, name="supprimer_commande"),

    # --- API Commandes (côté client) ---
    path("api/commandes/<int:produit_id>/passer/", views_api.api_passer_commande, name="api_passer_commande"),
    path("api/commandes/<int:id>/", views_api.api_consulter_commande, name="api_consulter_commande"),
    path("api/commandes/annulees/", views_api.api_commandes_annulees, name="api_commandes_annulees"),
    path("api/commandes/client/", views_api.api_client_commandes, name="api_client_commandes"),
    path("api/commandes/<int:id>/delete/", views_api.api_supprimer_commande, name="api_supprimer_commande"),
    path("api/commandes/<int:id>/annuler-client/", views_api.api_annuler_commande_client, name="api_annuler_commande_client"),
    path("api/commande/panier/ajouter/", views_api.ajouter_au_panier, name="ajouter_au_panier"),
    # path("api/commande/panier/consulter/", views_api.api_consulter_panier, name="api_consulter_panier"),
    path("api/commande/panier/vider/", views_api.vider_panier, name="vider_panier"),


    # --- API Commandes (côté admin) ---
    path("api/commandes/", views_api.api_gestion_commandes, name="api_gestion_commandes"),
    path("api/commandes/<int:id>/detail-admin/", views_api.api_detail_commande_admin, name="api_detail_commande_admin"),
    path("api/commandes/<int:id>/valider/", views_api.api_valider_commande, name="api_valider_commande"),
    path("api/commandes/<int:id>/annuler/", views_api.api_annuler_commande, name="api_annuler_commande"),
    path("api/commandes-validees-admin/", views_api.api_commandes_validees_admin, name="api_commandes_validees_admin"),
    path("api/commandes-annulees-admin/", views_api.api_commandes_annulees_admin, name="api_commandes_annulees_admin"),
]