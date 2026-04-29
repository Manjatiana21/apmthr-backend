from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from comptes.models import Notification
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.utils import timezone
from paiements.models import Paiement
from .models import Facture
from .serializers import FactureSerializer,FactureListSerializer
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.http import HttpResponse
from django.templatetags.static import static
import os
from django.conf import settings


# Génération d’un numéro unique basé sur le paiement
def generate_facture_number(paiement):
    count = Facture.objects.filter(paiement=paiement).count() + 1
    return f"FAC-{paiement.id}-{count}"


# Générer une facture (Admin uniquement)
@api_view(["POST"])
@permission_classes([IsAdminUser])
def api_generer_facture(request, paiement_id):
    paiement = get_object_or_404(Paiement, id=paiement_id)
    commande = paiement.commande

    # Vérifier conditions
    if paiement.statut != "REÇU":
        return Response({"error": "Paiement non reçu."}, status=400)

    if commande.statut not in ["VALIDEE", "VALIDÉE"]:
        return Response({"error": "Commande non validée."}, status=400)

    if hasattr(commande, "facture"):
        return Response({"error": "Une facture existe déjà pour cette commande."}, status=400)

    # Générer un numéro unique
    import uuid
    numero_facture = f"FAC-{commande.id}-{uuid.uuid4().hex[:6].upper()}"

    facture = Facture.objects.create(
        commande=commande,
        paiement=paiement,
        numero=numero_facture,
        montant_total=paiement.montant
    )

    serializer = FactureSerializer(facture)
    return Response(serializer.data, status=201)


# Télécharger une facture en PDF (Client ou Admin)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_facture_pdf(request, facture_id):
    facture = get_object_or_404(Facture, id=facture_id)
    if request.user.role != "ADMIN" and facture.commande.client != request.user:
        return Response({"error": "Vous n'avez pas accès à cette facture."}, status=403)
    
    for detail in facture.commande.details.all():
        detail.total = detail.quantite * detail.prix_unitaire
        
    
    html = render_to_string("factures/facture_template.html", {"facture": facture})

        # chemin absolu vers le logo
    logo_path = os.path.join(settings.BASE_DIR, "static", "images", "Logo.png")

    html = render_to_string("factures/facture_template.html", {
        "facture": facture,
        "logo_path": logo_path,
    })
    
        #Charger le CSS en mémoire
    css_path = os.path.join(settings.BASE_DIR, "static", "css", "Facture.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        html = f"<style>{css_content}</style>" + html


    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="facture_{facture.numero}.pdf"'
    pisa.CreatePDF(html, dest=response)
    return response



# Détail d’une facture
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_facture_detail(request, facture_id):
    facture = get_object_or_404(Facture, id=facture_id)
    if request.user.role != "ADMIN" and facture.commande.client != request.user:
        return Response({"error": "Vous n'avez pas accès à cette facture."}, status=403)
    serializer = FactureSerializer(facture)
    return Response(serializer.data)


# Envoyer une facture (Admin)
@api_view(["POST"])
@permission_classes([IsAdminUser])
def api_envoyer_facture(request, facture_id):
    facture = get_object_or_404(Facture, id=facture_id)
    facture.envoyee = True
    facture.save()

    Notification.objects.create(
        utilisateur=facture.commande.client,
        message=f"Nouvelle facture N° {facture.numero} disponible",
        lien=f"/mes-factures/{facture.id}"
    )
    return Response({"success": f"Facture {facture.numero} envoyée au client."})


# Liste des factures envoyées pour un client
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_mes_factures(request):
    factures = Facture.objects.filter(commande__client=request.user)
    print("Utilisateur connecté:", request.user.id, request.user.username)
    print("Factures trouvées:", factures.count())
    serializer = FactureListSerializer(factures, many=True)
    print("Données sérialisées:", serializer.data)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def api_factures_list(request):
    factures = Facture.objects.all().order_by("-date_emission")
    serializer = FactureSerializer(factures, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_factures_recues(request):
    # On filtre uniquement les factures envoyées par l’admin
    factures = Facture.objects.filter(commande__client=request.user, envoyee=True)
    serializer = FactureListSerializer(factures, many=True)
    return Response(serializer.data)