from django.urls import path
from . import views, views_api


urlpatterns = [
    # Côté client
    path("consulter/", views.consulter_paiement, name="consulter_paiement"),

    # Côté admin
    path("gestion/", views.gestion_paiements, name="gestion_paiement"),
    path("paiement/<int:paiement_id>/valider/", views.valider_paiement, name="valider_paiement"),
    path("paiement/<int:paiement_id>/annuler/", views.annuler_paiement, name="annuler_paiement"),
    path("facture/<int:paiement_id>/", views.facture_paiement, name="facture_paiement"),
    
    path("api/paiements/<int:paiement_id>/facture/pdf/", views_api.api_facture_paiement_pdf, name="api_facture_paiement_pdf"),

    path("api/paiements/client/", views_api.api_consulter_paiements_client, name="api_consulter_paiements_client"),
    path("api/gestion-paiements/", views_api.api_gestion_paiements, name="api_gestion_paiements"), 
    path("api/paiements/<int:paiement_id>/valider/", views_api.api_valider_paiement, name="api_valider_paiement"), 
    path("api/paiements/<int:paiement_id>/annuler/", views_api.api_annuler_paiement, name="api_annuler_paiement"),
    path("api/paiements/<int:paiement_id>/changer-stat/", views_api.api_changer_statut_paiement, name="api_changer_statut_paiement"),
    path("api/paiements/<int:paiement_id>/facture/", views_api.api_facture_paiement, name="api_facture_paiement"),

    path("api/comptes/paiements/<int:paiement_id>/", views_api.api_paiement_detail, name="api_paiement_detail"),
    path("api/comptes/paiements/<int:paiement_id>/generer-facture/", views_api.api_generer_facture, name="api_generer_facture"),
]
