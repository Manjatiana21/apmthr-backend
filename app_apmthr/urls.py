"""
URL configuration for app_apmthr project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from livraisons.views_api import LivraisonViewSet
from stocks.views_api import MouvementStockViewSet
from comptes.views_api import UtilisateurViewSet, NotificationViewSet
from paiements.views_api import ModePaiementViewSet, PaiementViewSet
from catalogue.views_api import ProduitViewSet, TypeProduitViewSet, FournisseurViewSet
from commandes.views_api import CommandeViewSet, DetailsViewSet, CommandeItemViewSet
from rest_framework.routers import DefaultRouter

router = routers.DefaultRouter()

router.register(r'produits', ProduitViewSet)
router.register(r'types-produits', TypeProduitViewSet)
router.register(r'fournisseurs', FournisseurViewSet)

router.register(r'commandes', CommandeViewSet)
router.register(r'details', DetailsViewSet) 
router.register(r'items', CommandeItemViewSet)

router.register(r'livraisons', LivraisonViewSet, basename="livraison")

router.register(r'mouvements-stock', MouvementStockViewSet)

router.register(r'modes-paiement', ModePaiementViewSet) 
router.register(r'paiements', PaiementViewSet,basename="paiement")

router.register(r'notifications', NotificationViewSet)
router.register(r'utilisateurs', UtilisateurViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    
    path("", include("commandes.urls")),
    path("", include("catalogue.urls")),
    path("", include("comptes.urls")),
    path("", include("livraisons.urls")),
    path("", include("paiements.urls")),
    path("", include("stocks.urls")),
    path("", views.home, name="home"),
    path("api/comptes/", include("factures.urls")),
    path("", include("factures.urls")),
    path("api/", include("livraisons.urls")), 


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
