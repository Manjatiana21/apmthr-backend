from django.shortcuts import render, get_object_or_404, redirect
from .models import Paiement
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from comptes.models import Notification
from django.urls import reverse
from django.http import HttpResponse 
from django.template.loader import render_to_string 
from xhtml2pdf import pisa
from django.template.loader import get_template

# Create your views here.
OPERATEURS_NUMEROS={
    "MVola":"034 09 071 90",
}

@login_required
def consulter_paiement(request):
    paiements = Paiement.objects.filter(client=request.user).order_by('-date_paiement')
    return render(request, "paiements/consulter_paiement.html", {"paiements": paiements})

@login_required
def gestion_paiements(request):
    paiements = Paiement.objects.all().order_by('-date_paiement')
    return render(request, "paiements/gestion_paiement.html", {"paiements": paiements})


@login_required
def valider_paiement(request, paiement_id):
    paiement = get_object_or_404(Paiement, id=paiement_id)
    paiement.validerPaiement()
    Notification.objects.create(
        utilisateur=paiement.client,
        message=f"Votre paiement pour la commande {paiement.commande.details.first().produit.designation} a été validé.",
        lien=reverse("facture_paiement", args=[paiement.id]) 
    )


    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"success": True, "statut": paiement.statut})
    
    return redirect("gestion_paiements")

@login_required
def annuler_paiement(request, paiement_id):
    paiement = get_object_or_404(Paiement, id=paiement_id)
    paiement.annulerPaiement()
    Notification.objects.create(
        utilisateur=paiement.client,
        message=f"Votre paiement pour la commande #{paiement.commande.id} a été annulé."
               
    )
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"success": True, "statut": paiement.statut})
    return redirect("gestion_paiement")


def changer_statut_paiement(request, id):
    paiement = get_object_or_404(Paiement, id=id)
    paiement.changerStatutPaiement('CONFIRME')
    return redirect('consulter_paiement', id=id)

@login_required
def consulter_paiement(request):
    paiements = Paiement.objects.filter(client=request.user).order_by('-date_paiement')
    return render(request, "paiements/consulter_paiement.html", {"paiements": paiements})



@login_required
def facture_paiement(request, paiement_id):
    paiement = get_object_or_404(Paiement, id=paiement_id)
    commande = paiement.commande
    details = commande.details.all()

    return render(request, "paiements/facture.html", {
        "paiement": paiement,
        "commande": commande,
        "details": details,
    })


