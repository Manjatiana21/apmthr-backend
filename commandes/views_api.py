from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Commande, Details, CommandeItem
from .serializers import CommandeSerializer, DetailsSerializer, CommandeItemSerializer, PanierSerializer
from catalogue.models import Produit
from comptes.models import Notification, Utilisateur
from livraisons.models import Livraison
from livraisons.serializers import LivraisonSerializer
from paiements.models import ModePaiement, Paiement



# ViewSets
class CommandeViewSet(viewsets.ModelViewSet):
    queryset = Commande.objects.all().order_by('-date_commande')
    serializer_class = CommandeSerializer

    @action(detail=False, methods=["get"], url_path="client")
    def client_commandes(self, request):
        commandes = Commande.objects.filter(client=request.user).order_by("-date_commande")
        serializer = self.get_serializer(commandes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="consulter")
    def consulter_commande(self, request, pk=None):
        commande = get_object_or_404(Commande, id=pk, client=request.user)
        serializer = self.get_serializer(commande)
        return Response(serializer.data)
    
    @action(detail=True, methods=["post"], url_path="annuler-client")
    def annuler_client(self, request, pk=None):
        commande = get_object_or_404(Commande, id=pk, client=request.user)

        if commande.statut not in ["EN_ATTENTE"]:
            return Response({"detail": "Impossible d'annuler cette commande"}, status=status.HTTP_400_BAD_REQUEST)

        commande.statut = "ANNULEE"
        commande.save()

        # admins = Utilisateur.objects.filter(role="ADMIN")
        # for admin in admins:
        #     Notification.objects.create(
        #         utilisateur=admin,
        #         message=f"{request.user.username} a annulé sa commande #{commande.id}."
        #     )

        serializer = self.get_serializer(commande)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="annulees")
    def commandes_annulees(self, request):
        commandes = Commande.objects.filter(client=request.user, statut="ANNULEE").order_by("-date_commande")
        serializer = self.get_serializer(commandes, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

    @action(detail=False, methods=['delete'], url_path='effacer-selection')
    def effacer_selection(self, request):
        ids = request.data.get("ids", [])
        Commande.objects.filter(id__in=ids, statut="ANNULEE").delete()
        return Response({"message": "Commandes sélectionnées supprimées"}, status=status.HTTP_204_NO_CONTENT)


class DetailsViewSet(viewsets.ModelViewSet):
    queryset = Details.objects.all()
    serializer_class = DetailsSerializer


class CommandeItemViewSet(viewsets.ModelViewSet):
    queryset = CommandeItem.objects.all()
    serializer_class = CommandeItemSerializer

# API côté Admin
@api_view(["GET"])
@permission_classes([IsAdminUser])
def api_gestion_commandes(request):
    commandes = Commande.objects.all().order_by("-date_commande")
    serializer = CommandeSerializer(commandes, many=True)
    return Response(serializer.data)

 
@api_view(["POST"])
@permission_classes([IsAdminUser])
def api_valider_commande(request, id):
    commande = get_object_or_404(Commande, id=id)
    commande.validerCommande()

    # notification client
    # Notification.objects.create(
    #     utilisateur=commande.client,
    #     message=f"Votre commande #{commande.id} a été validée par l’admin."
    # )

    # # notification admin
    # admins = Utilisateur.objects.filter(role="ADMIN")
    # for admin in admins:
    #     Notification.objects.create(
    #         utilisateur=admin,
    #         message=f"Commande #{commande.id} validée pour {commande.client.username}."
    #     )

    # création livraison si elle n’existe pas
    livraison, created = Livraison.objects.get_or_create(
        commande=commande,
        defaults={"statut": "NON_DEMARREE"}
    )

    serializer = CommandeSerializer(commande)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def api_annuler_commande(request, id):
    commande = get_object_or_404(Commande, id=id)
    commande.annulerCommande()

    # # notification client
    # Notification.objects.create(
    #     utilisateur=commande.client,
    #     message=f"Votre commande #{commande.id} a été annulée par l’admin."
    # )

    # # notification admin
    # admins = Utilisateur.objects.filter(role="ADMIN")
    # for admin in admins:
    #     Notification.objects.create(
    #         utilisateur=admin,
    #         message=f"Commande #{commande.id} annulée pour {commande.client.username}."
    #     )

    serializer = CommandeSerializer(commande)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAdminUser])
def api_detail_commande_admin(request, id):
    commande = get_object_or_404(Commande, id=id)
    serializer = CommandeSerializer(commande)
    return Response(serializer.data)


# API côté Client
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_passer_commande(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    quantite = int(request.data.get("quantite", 1))

    mode_paiement_id = request.data.get("mode_paiement")
    mode = get_object_or_404(ModePaiement, id=mode_paiement_id) if mode_paiement_id else None

    commande = Commande.objects.create(
        client=request.user,
        statut="EN_ATTENTE",
        mode_paiement=mode,
        adresse_livraison=request.data.get("adresse_livraison"),
    )

    Details.objects.create(
        commande=commande,
        produit=produit,
        quantite=quantite,
        prix_unitaire=produit.prix
    )

    commande.calculerTotal()
    commande.creerCommande()

    Paiement.objects.create(
        commande=commande,
        client=request.user,
        mode_paiement=mode,
        montant=commande.total,
        statut="EN_ATTENTE",
        date_paiement=None
    )


    commande.refresh_from_db()
    return Response(CommandeSerializer(commande).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_consulter_commande(request, id):
    commande = get_object_or_404(Commande, id=id, client=request.user)
    serializer = CommandeSerializer(commande)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_client_commandes(request):
    commandes = Commande.objects.filter(client=request.user).order_by("-date_commande")
    serializer = CommandeSerializer(commandes, many=True)
    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_annuler_commande_client(request, id):
    commande = get_object_or_404(Commande, id=id, client=request.user)

    if commande.statut not in ["EN_ATTENTE"]:  
        return Response({"detail": "Impossible d'annuler cette commande"}, status=400)

    commande.annulerCommande(par_client=True)

    # ✅ notification admin
    # admins = Utilisateur.objects.filter(role="ADMIN")
    # for admin in admins:
    #     Notification.objects.create(
    #         utilisateur=admin,
    #         message=f"{request.user.username} a annulé sa commande #{commande.id}."
    #     )

    serializer = CommandeSerializer(commande)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_commandes_annulees(request):
    commandes = Commande.objects.filter(client=request.user, statut__in=["ANNULEE"]).order_by("-date_commande")
    serializer = CommandeSerializer(commandes, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def api_commandes_annulees_admin(request):
    commandes = Commande.objects.filter(statut="ANNULEE").order_by("-date_commande")
    serializer = CommandeSerializer(commandes, many=True)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAdminUser])
def api_commandes_validees_admin(request):
    commandes = Commande.objects.filter(statut="VALIDEE").order_by("-date_commande")
    serializer = CommandeSerializer(commandes, many=True)
    return Response(serializer.data)

@api_view(["DELETE"])
def api_supprimer_commande(request, id):
    commande = get_object_or_404(Commande, id=id)

    # ✅ sécurité : empêcher suppression si paiements liés
    if Paiement.objects.filter(commande=commande).exists():
        return Response({"error": "Impossible de supprimer : des paiements sont liés."}, status=400)

    commande.delete()
    return Response({"success": True, "message": f"Commande #{id} supprimée avec succès."}, status=204)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ajouter_au_panier(request):
    """
    Ajoute une commande simple ou un panier multi-produits.
    """
    serializer = PanierSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        commande = serializer.save()

        # ✅ Créer un paiement lié à la commande (comme dans api_passer_commande)
        if commande.mode_paiement:
            Paiement.objects.create(
                commande=commande,
                client=request.user,
                mode_paiement=commande.mode_paiement,
                montant=commande.total,
                statut="EN_ATTENTE",
                date_paiement=None
            )

        # ✅ Notifications client + admin
        commande.creerCommande()

        return Response(
            {
                "detail": "Commande créée avec succès.",
                "commande": CommandeSerializer(commande).data,
            },
            status=status.HTTP_201_CREATED,
        )
    else:
        # ✅ log côté serveur pour diagnostic
        print("Erreurs serializer:", serializer.errors)
        return Response(
            {"errors": serializer.errors, "detail": "Payload invalide."},
            status=status.HTTP_400_BAD_REQUEST,
        )


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def api_consulter_panier(request):
#     commande = Commande.objects.filter(client=request.user, statut="EN_ATTENTE").last()
#     if not commande:
#         return Response({"detail": "Aucun panier en cours."}, status=404)
#     serializer = CommandeSerializer(commande)
#     return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def vider_panier(request):
    commande = Commande.objects.filter(client=request.user, statut="EN_ATTENTE").last()
    if not commande:
        return Response({"detail": "Aucun panier en cours."}, status=404)

    # ✅ Supprimer uniquement les détails (produits) du panier
    commande.details.all().delete()

    # ✅ Réinitialiser le total
    commande.total = 0
    commande.save()

    return Response({"detail": "Panier vidé avec succès."}, status=200)
