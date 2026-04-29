from django.urls import path
from django.contrib.auth import views as auth_views
from .views_api import api_admin_stats
from . import views, views_api
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    # Templates Django
    path("espace-client/", views.espace_client, name="espace_client"),
    path("tableau-admin/", views.tableau_de_bord_admin, name="tableau_admin"),
    path("inscription/", views.inscription_client, name="inscription"),
    path("connexion/", views.login_view, name="authentification"),
    path("logout/", auth_views.LogoutView.as_view(next_page="authentification"), name="logout"),
    path("notifications/", views.mes_notifications, name="mes_notifications"),
    path("notifications/admin/", views.notifications_admin, name="notifications_admin"),


   
    # 🔔 Notifications Client
    path("api/comptes/mes-notifications/", views_api.api_mes_notifications, name="api_mes_notifications"),
    path("api/comptes/notifications/marquer-tout-lu/", views_api.api_marquer_tout_lu, name="api_marquer_tout_lu"),
    path("api/comptes/notifications/<int:notif_id>/marquer-lue/", views_api.api_marquer_notif_lue, name="api_marquer_notif_lue"),

    # 🔔 Notifications Admin
    path("api/comptes/notifications/admin/", views_api.api_notifications_admin, name="api_notifications_admin"),

    
        # 👥 Gestion des utilisateurs (Admin)
    path("api/comptes/utilisateurs/", views_api.api_utilisateurs, name="api_utilisateurs"),
    path("api/comptes/utilisateurs/<int:user_id>/suspendre/", views_api.api_suspendre_utilisateur, name="api_suspendre_utilisateur"),
    path("api/comptes/utilisateurs/<int:user_id>/reactiver/", views_api.api_reactiver_utilisateur, name="api_reactiver_utilisateur"),

    # API React
    path("api/admin/stats/", api_admin_stats, name="api_admin_stats"),
    path("api/comptes/login/", views_api.login_view, name="login_api"),
    path("api/comptes/register/", views_api.register_view, name="register_api"),
    path("api/comptes/logout/", views_api.api_logout, name="api_logout"),
   
    
    path("profil/modifier-nom/", views_api.modifier_nom, name="modifier_nom"),
    path("profil/modifier-telephone/", views_api.modifier_telephone, name="modifier_telephone"),
    path("profil/modifier-adresse/", views_api.modifier_adresse, name="modifier_adresse"),
    path("profil/modifier-email/", views_api.modifier_email, name="modifier_email"),
    path("profil/modifier-motdepasse/", views_api.modifier_motdepasse, name="modifier_motdepasse"),

    path("api/comptes/notifications/<int:notif_id>/lu/", views_api.api_marquer_notif_lue, name="api_marquer_notif_lue"),
    path("api/comptes/paiements/", views_api.api_mes_paiements, name="api_mes_paiements"),
    #client connecté
    path("api/me/", views_api.me_view, name="me_api"),

    path("api/comptes/paiements/admin/", views_api.api_gestion_paiements, name="api_gestion_paiements"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"), 
]
