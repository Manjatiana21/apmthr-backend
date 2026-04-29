from django.urls import path
from . import views, views_api

urlpatterns = [
    path("admin/", views.liste_livraisons_admin, name="liste_livraisons_admin"),
    path("planifier/<int:commande_id>/", views.planifier_livraison, name="planifier_livraison"),
    path("terminer/<int:livraison_id>/", views.terminer_livraison, name="terminer_livraison"),
    path("client/", views.liste_livraisons_client, name="liste_livraisons_client"),

    #
    path("api/livraisons/admin/", views_api.api_liste_livraisons_admin, name="api_liste_livraisons_admin"),
    path("api/livraisons/client/", views_api.api_liste_livraisons_client, name="api_liste_livraisons_client"),
    path("api/livraisons/<int:livraison_id>/demarrer/", views_api.api_demarrer_livraison, name="api_demarrer_livraison"),
    path("api/livraisons/<int:livraison_id>/terminer/", views_api.api_terminer_livraison, name="api_terminer_livraison"),
    path("api/livraisons/<int:commande_id>/planifier/", views_api.api_planifier_livraison, name="api_planifier_livraison"),
    path("livraisons/<int:pk>/update-statut/", views.update_livraison_statut, name="update_livraison_statut"), 

]
