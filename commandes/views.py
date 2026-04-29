from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from catalogue.models import Produit
from .models import Commande, Details
from .forms import CommandeCompleteForm
from stocks.models import MouvementStock
from django.contrib import messages
from paiements.models import Paiement
from paiements.models import ModePaiement, Paiement
from livraisons.models import Livraison
from django.http import JsonResponse


@login_required
def gestion_commandes(request):
    if not request.user.is_authenticated or request.user.role != "ADMIN":
        return redirect("espace_client")
    else:
        commandes = Commande.objects.all().order_by("-date_commande")
        return render(request, 'commandes/gestion_commandes.html', {'commandes': commandes})

@login_required
def passer_commande(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)

    if request.method == 'POST':
        form = CommandeCompleteForm(request.POST)
        if form.is_valid():
            # nouvelle commande
            commande = form.save(commit=False)
            commande.client = request.user
            commande.statut = "EN_ATTENTE"
            commande.produit = produit
            commande.save()

            
            quantite = int(request.POST.get("quantite", 1))
            Details.objects.create(
                commande=commande,
                produit=produit,
                quantite=quantite,
                prix_unitaire=produit.prix
            )

            # recalcul du total
            commande.calculerTotal()

            # création du paiement lié
            paiement, created = Paiement.objects.get_or_create(
                commande=commande,
                defaults={
                    "client": request.user,
                    "montant": commande.total,
                    "mode_paiement": commande.mode_paiement,
                    "statut": "EN_ATTENTE",
                }
            )

            # messages utilisateur
            if commande.statut == "VALIDEE":
                messages.success(request, f"Votre commande #{commande.id} a été validée avec succès.")
            elif commande.statut == "EN_ATTENTE":
                messages.warning(request, f"Votre commande #{commande.id} est mise en attente car le stock est insuffisant.")
            elif commande.statut == "ANNULEE":
                messages.error(request, f"Votre commande #{commande.id} a été annulée (stock insuffisant).")

            return redirect("consulter_commande", id=commande.id)  
    else:
        form = CommandeCompleteForm()

   
    modes = ModePaiement.objects.all()
    return render(request, "commandes/passer_commande.html", {
        "form": form,
        "produit": produit,
        "modes": modes,
    })




@login_required
def consulter_commande(request, id):
    commande = get_object_or_404(Commande, id=id, client=request.user)
    details = commande.details.all()
    return render(request, "commandes/consulter_commande.html", {
        "commande": commande,
        "details": details,
    })


@login_required 
def client_commande(request):
    commandes = Commande.objects.filter(client=request.user).order_by("-date_commande").exclude(statut="ANNULEE")
    return render(request, "commandes/client_commandes.html", {"commandes": commandes})


@login_required
def commandes_annulees(request):
    commandes = Commande.objects.filter( client=request.user, statut__in=["ANNULEE"] ).order_by("-date_commande")
    return render(request, "commandes/commandes_annulees.html", {"commandes": commandes})


@login_required
def detail_commande_admin(request, id):
    commande = get_object_or_404(Commande, id=id)
    details = commande.details.all() 

    return render(request, "commandes/detail_commande_admin.html", {
        "commande": commande,
        "details": details,
    })


@login_required
def valider_commande(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    commande.statut = "VALIDEE"
    commande.save()

    Livraison.objects.get_or_create(
        commande=commande,
        defaults={
            "statut": "NON_DEMARREE"
        }
    )

@login_required
def annuler_commande(request, id):
    commande = get_object_or_404(Commande, id=id)
    commande.annulerCommande() 
    return redirect("gestion_commandes")

    commande.status = "ANNULEE"
    commande.save()

    Notification.objects.create(
        utilisateur=commande.client,
        message=f"Votre commande ({commande.produit} x{commande.quantite}) a été annulée par l’admin."
    )

    admin = Utilisateur.objects.filter(role="ADMIN").first()
    Notification.objects.create(
        utilisateur=admin,
        message=f"Commande annulée par l’admin pour {commande.client.username} : {commande.produit} x{commande.quantite}"
    )

    return Response({"success": True, "message": "Commande annulée et notifications créées."})


@login_required
def supprimer_commande(request, id):
    if request.method == "DELETE":
        commande = get_object_or_404(Commande, id=id)

        if Paiement.objects.filter(commande=commande).exists():
            return JsonResponse({"error": "Impossible de supprimer : des paiements sont liés."}, status=400)

        commande.delete()
        return JsonResponse({"success": True, "message": f"Commande #{id} supprimée avec succès."}, status=204)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)
