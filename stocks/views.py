from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from .models import MouvementStock
from .forms import MouvementStockForm
from django.db.models import Sum

def gestion_stock(request):
    if not request.user.is_staff and getattr(request.user, "role", None) != "ADMIN":
        return HttpResponseForbidden("Accès réservé à l'administrateur.")

    mouvements = MouvementStock.objects.all().order_by('-date_mouvement') 
    return render(request, "stocks/gestion_stock.html", {"mouvements": mouvements})

def ajouter_mouvement(request):
    if request.method == 'POST':
        form = MouvementStockForm(request.POST)
        if form.is_valid():
            mvt = form.save()
            return redirect("historique_stock", produit_id=mvt.produit.id)
    else:
        form = MouvementStockForm()
    return render(request, "stocks/historique_stock.html", {'form': form})

def historique_stock(request, produit_id):
    mouvements = MouvementStock.objects.filter(produit_id=produit_id)
    return render(request, "stocks/historique_stock.html", {'mouvements': mouvements})

def rapport_mouvements(request):
    if not request.user.is_authenticated or getattr(request.user, "role", None) != "ADMIN":
        return HttpResponseForbidden("Accès réservé aux administrateurs.")

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

    return render(request, "stocks/rapport_mouvement.html", {
        "data": data,
        "mouvements": mouvements
    })

