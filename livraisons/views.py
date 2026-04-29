from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Livraison
from commandes.models import Commande  # important pour planifier_livraison
from rest_framework.decorators import api_view, permission_classes
from .serializers import LivraisonSerializer

@login_required
def liste_livraisons_admin(request):
    if request.user.role == "ADMIN":
        livraisons = Livraison.objects.select_related("commande").all().order_by("-date_mise_a_jour")
    else:
        livraisons = []
    return render(request, "livraisons/liste_admin.html", {"livraisons": livraisons})


@login_required
def liste_livraisons_client(request):
    if request.user.role == "CLIENT":
        livraisons = Livraison.objects.select_related("commande").filter(
            commande__client=request.user
        ).order_by("-date_prevue")
    else:
        livraisons = []
    return render(request, "livraisons/liste_client.html", {"livraisons": livraisons})


@login_required
def demarrer_livraison(request, livraison_id):
    if request.user.role == "ADMIN":
        livraison = get_object_or_404(Livraison, id=livraison_id)
        livraison.demarrer()
    return redirect("liste_livraisons_admin")


@login_required
def terminer_livraison(request, livraison_id):
    if request.user.role == "ADMIN":
        livraison = get_object_or_404(Livraison, id=livraison_id)
        livraison.terminer()
    return redirect("liste_livraisons_admin")


@login_required
def planifier_livraison(request, commande_id):
    if request.user.role == "ADMIN":
        commande = get_object_or_404(Commande, id=commande_id)
        livraison, created = Livraison.objects.get_or_create(commande=commande)
        livraison.planifier(delai_heures=48)  # par défaut 48h
        return redirect("liste_livraisons_admin")
    else:
        return redirect("home")

@api_view(["PATCH"])
def update_livraison_statut(request, pk):
    livraison = get_object_or_404(Livraison, pk=pk)
    nouveau_statut = request.data.get("statut")

    if not nouveau_statut:
        return Response({"error": "Champ 'statut' manquant"}, status=400)

    if nouveau_statut == "EN_COURS":
        livraison.planifier()
    elif nouveau_statut == "LIVREE":
        livraison.terminer()
    elif nouveau_statut in ["NON_DEMARREE", "EN_COURS", "LIVREE"]:
        livraison.statut = nouveau_statut
        livraison.save()
    else:
        return Response({"error": "Statut invalide"}, status=400)

    serializer = LivraisonSerializer(livraison)
    return Response(serializer.data)
