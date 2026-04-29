from rest_framework import viewsets, status
from .models import Produit, TypeProduit, Fournisseur
from .serializers import ProduitSerializer, TypeProduitSerializer, FournisseurSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.decorators import action

class ProduitViewSet(viewsets.ModelViewSet):
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer

    def get_queryset(self):
        queryset = Produit.objects.all()
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")
        return queryset

    def destroy(self, request, *args, **kwargs):
        """Au lieu de supprimer, on archive le produit"""
        produit = self.get_object()
        produit.is_active = False
        produit.save()
        return Response({"success": "Produit archivé"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def reactiver(self, request, pk=None):
        """Réactive un produit archivé"""
        produit = self.get_object()
        produit.is_active = True
        produit.save()
        return Response(ProduitSerializer(produit).data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save(is_active=True)


class TypeProduitViewSet(viewsets.ModelViewSet):
    queryset = TypeProduit.objects.all()
    serializer_class = TypeProduitSerializer

class FournisseurViewSet(viewsets.ModelViewSet):
    queryset = Fournisseur.objects.all()
    serializer_class = FournisseurSerializer


@api_view(["GET"])
def api_liste_produits(request):
    produits = Produit.objects.all()
    serializer = ProduitSerializer(produits, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def api_detail_produit(request, id):
    try:
        produit = Produit.objects.get(id=id)
    except Produit.DoesNotExist:
        return Response({"error": "Produit introuvable"}, status=404)
    serializer = ProduitSerializer(produit)
    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAdminUser])
def api_ajouter_produit(request):
    serializer = ProduitSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(is_active=True)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(["PUT"])
@permission_classes([IsAdminUser])
def api_modifier_produit(request, id):
    try:
        produit = Produit.objects.get(id=id)
    except Produit.DoesNotExist:
        return Response({"error": "Produit introuvable"}, status=404)
    serializer = ProduitSerializer(produit, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def api_supprimer_produit(request, id):
    try:
        produit = Produit.objects.get(id=id)
    except Produit.DoesNotExist:
        return Response({"error": "Produit introuvable"}, status=404)
    produit.delete()
    return Response({"success": "Produit supprimé"}, status=204)


@api_view(["GET"])
def api_produits_par_type(request, type_id):
    produits = Produit.objects.filter(type_produit_id=type_id)
    serializer = ProduitSerializer(produits, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def types_produits_list(request):
    qs = TypeProduit.objects.all()
    serializer = TypeProduitSerializer(qs, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def fournisseurs_list(request):
    qs = Fournisseur.objects.all()
    serializer = FournisseurSerializer(qs, many=True)
    return Response(serializer.data)

