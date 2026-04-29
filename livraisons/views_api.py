from rest_framework import viewsets, filters
from .models import Livraison
from .serializers import LivraisonSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view, permission_classes 
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from commandes.models import Commande
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

class LivraisonViewSet(viewsets.ModelViewSet):
    queryset = Livraison.objects.all().order_by("-date_mise_a_jour")
    serializer_class = LivraisonSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    permission_classes = [IsAuthenticated]

    filterset_fields = ["statut", "commande__client__username"]
    search_fields = ["commande__id", "adresse_livraison"]
    ordering_fields = ["date_prevue"]



    @action(detail=False, methods=["get"], url_path="client")
    def livraisons_client(self, request):
        livraisons = Livraison.objects.filter(commande__client=request.user).order_by("-date_prevue")
        serializer = self.get_serializer(livraisons, many=True)
        return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def api_liste_livraisons_admin(request):
    livraisons = Livraison.objects.select_related("commande").all().order_by("-date_prevue")
    serializer = LivraisonSerializer(livraisons, many=True)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_liste_livraisons_client(request):
    livraisons = Livraison.objects.select_related("commande").filter(
        commande__client=request.user
    ).order_by("-date_prevue")
    serializer = LivraisonSerializer(livraisons, many=True)
    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAdminUser])
def api_demarrer_livraison(request, livraison_id):
    livraison = get_object_or_404(Livraison, id=livraison_id)
    livraison.demarrer()
    serializer = LivraisonSerializer(livraison)
    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAdminUser])
def api_terminer_livraison(request, livraison_id):
    livraison = get_object_or_404(Livraison, id=livraison_id)
    livraison.terminer()
    serializer = LivraisonSerializer(livraison)
    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAdminUser])
def api_planifier_livraison(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)
    livraison, created = Livraison.objects.get_or_create(commande=commande)
    livraison.planifier(delai_heures=48)  # par défaut 48h
    serializer = LivraisonSerializer(livraison)
    return Response(serializer.data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def api_update_livraison_statut(request, livraison_id):
    livraison = get_object_or_404(Livraison, id=livraison_id)

    nouveau_statut = request.data.get("statut")
    if not nouveau_statut:
        return Response({"error": "Statut requis"}, status=status.HTTP_400_BAD_REQUEST)

    # Vérifier que le statut est valide
    statuts_valides = ["NON_DEMARRE", "EN_COURS", "LIVRE"]
    if nouveau_statut not in statuts_valides:
        return Response({"error": "Statut invalide"}, status=status.HTTP_400_BAD_REQUEST)

    livraison.statut = nouveau_statut
    livraison.save()

    serializer = LivraisonSerializer(livraison)
    return Response(serializer.data, status=status.HTTP_200_OK)

def api_livraisons_admin(request):
    livraisons = Livraison.objects.filter(commande__statut="VALIDEE")
    serializer = LivraisonSerializer(livraisons, many=True)
    return Response(serializer.data)
