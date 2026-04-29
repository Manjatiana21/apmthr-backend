from django.urls import path
from . import views_api, views
from .views_api import api_factures_list
urlpatterns = [
    path("factures/<int:facture_id>/", views_api.api_facture_detail, name="api_facture_detail"),
    path("api/comptes/paiements/<int:paiement_id>/generer-facture/", views_api.api_generer_facture, name="api_generer_facture"),
    path("factures/<int:facture_id>/pdf/", views_api.api_facture_pdf, name="facture_pdf"),
    path("api/comptes/factures/<int:facture_id>/envoyer/", views_api.api_envoyer_facture, name="api_envoyer_facture"),
    path("factures/", api_factures_list, name="api_factures_list"),
    path("api/comptes/factures/recues/", views_api.api_factures_recues, name="api_factures_recues"),
]
