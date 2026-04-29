from django.urls import path
from . import views_api

urlpatterns = [
    path("admin/", views_api.api_liste_livraisons_admin, name="api_liste_livraisons_admin"),
    path("client/", views_api.api_liste_livraisons_client, name="api_liste_livraisons_client"),
    path("<int:livraison_id>/demarrer/", views_api.api_demarrer_livraison, name="api_demarrer_livraison"),
    path("<int:livraison_id>/terminer/", views_api.api_terminer_livraison, name="api_terminer_livraison"),
    path("<int:commande_id>/planifier/", views_api.api_planifier_livraison, name="api_planifier_livraison"),
    path("<int:livraison_id>/update-statut/", views_api.api_update_livraison_statut, name="api_update_livraison_statut"),
]
