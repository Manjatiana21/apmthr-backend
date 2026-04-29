from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import MouvementStock
from .serializers import MouvementStockSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum
from django.utils.timezone import localtime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from django.shortcuts import get_object_or_404


class MouvementStockViewSet(viewsets.ModelViewSet):
    queryset = MouvementStock.objects.all().order_by('-date_mouvement')
    serializer_class = MouvementStockSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # ✅ filtres disponibles
    filterset_fields = ["type_mouvement", "produit__designation"]
    search_fields = ["produit__designation"]
    ordering_fields = ["date_mouvement", "quantite"]

@api_view(["GET"])
def rapport_mouvement(request):
    mouvements = MouvementStock.objects.all()

    # filtres
    type_mouvement = request.GET.get("type_mouvement")
    produit = request.GET.get("produit")

    if type_mouvement:
        mouvements = mouvements.filter(type_mouvement=type_mouvement)
    if produit:
        mouvements = mouvements.filter(produit__designation__icontains=produit)

    # regroupement par mois
    data = {}
    for mvt in mouvements:
        mois = localtime(mvt.date_mouvement).strftime("%Y-%m")
        if mois not in data:
            data[mois] = {"ENTREE": 0, "SORTIE": 0}
        data[mois][mvt.type_mouvement] += mvt.quantite

    return Response({
        "data": data,
        "mouvements": MouvementStockSerializer(mouvements, many=True).data
    })



@api_view(["GET"])
@permission_classes([IsAdminUser])
def api_gestion_stock(request):
    mouvements = MouvementStock.objects.all().order_by('-date_mouvement')
    serializer = MouvementStockSerializer(mouvements, many=True)
    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAdminUser])
def api_ajouter_mouvement(request):
    serializer = MouvementStockSerializer(data=request.data)
    if serializer.is_valid():
        mvt = serializer.save()
        return Response(MouvementStockSerializer(mvt).data, status=201)
    return Response(serializer.errors, status=400)

@api_view(["GET"])
@permission_classes([IsAdminUser])
def api_historique_stock(request, produit_id):
    mouvements = MouvementStock.objects.filter(produit_id=produit_id).order_by("-date_mouvement")
    serializer = MouvementStockSerializer(mouvements, many=True)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAdminUser])
def api_rapport_mouvements(request):
    mouvements = MouvementStock.objects.all().order_by("-date_mouvement")

    stats = MouvementStock.objects.values("type_mouvement", "date_mouvement__month").annotate(
        total=Sum("quantite")
    )

    data = {}
    for s in stats:
        mois = s["date_mouvement__month"]
        type_mvt = s["type_mouvement"]
        if mois not in data:
            data[mois] = {"ENTREE": 0, "SORTIE": 0}
        data[mois][type_mvt] = s["total"]

    return Response({
        "stats": data,
        "mouvements": MouvementStockSerializer(mouvements, many=True).data
    })
