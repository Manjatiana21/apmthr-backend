from django.shortcuts import render, get_object_or_404, redirect
from .models import Produit, TypeProduit, Fournisseur
from .forms import ProduitForm
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required


def liste_produits(request):
    produits = Produit.objects.all()
    return render(request, 'catalogue/liste_produits.html', {'produits': produits})

def detail_produit(request, id):
    produit = get_object_or_404(Produit, id=id)
    return render(request, 'catalogue/detail_produit.html', {'produit': produit})

def produits_par_type(request, type_id):
    produits = Produit.objects.filter(type_produit_id=type_id)
    return render(request, 'catalogue/liste_produits_par_type.html', {'produits': produits})

# Vérifie que l'utilisateur est admin
def est_admin(user):
    return user.is_staff  # ou user.is_superuser selon ta logique

@user_passes_test(est_admin)
def ajouter_produit(request):
    if request.method == "POST":
        form = ProduitForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Produit ajouté avec succès.")
            return redirect("liste_produits")
    else:
        form = ProduitForm()
    return render(request, "catalogue/ajouter_produit.html", {"form": form})



@login_required
def liste_des_produits(request):
    produits = Produit.objects.all()
    return render(request, "catalogue/listes_des_produits.html", {"produits": produits})


@login_required
def modifier_produit(request, id):
    produit = get_object_or_404(Produit, id=id)
    if request.method == "POST":
        form = ProduitForm(request.POST, instance=produit)
        if form.is_valid():
            form.save()
            messages.success(request, "Produit modifié avec succès.")
            return redirect("listes_des_produits")
    else:
        form = ProduitForm(instance=produit)
    return render(request, "catalogue/modifier_produit.html", {"form": form, "produit": produit})

@login_required
def supprimer_produit(request, id):
    produit = get_object_or_404(Produit, id=id)
    if request.method == "POST":
        produit.delete()
        messages.success(request, "Produit supprimé avec succès.")
        return redirect("listes_des_produits")
    return render(request, "catalogue/supprimer_produit.html", {"produit": produit})
