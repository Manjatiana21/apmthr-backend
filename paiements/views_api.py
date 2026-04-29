from rest_framework import viewsets
from .models import ModePaiement, Paiement
from .serializers import ModePaiementSerializer, PaiementSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse 
from django.template.loader import get_template 
from xhtml2pdf import pisa
from factures.models import Facture
from factures.serializers import FactureSerializer


# ViewSets (DRF standard)
class ModePaiementViewSet(viewsets.ModelViewSet):
    queryset = ModePaiement.objects.all()
    serializer_class = ModePaiementSerializer

class PaiementViewSet(viewsets.ModelViewSet):
    serializer_class = PaiementSerializer

    def get_queryset(self):
        return Paiement.objects.filter(commande__statut="VALIDEE").order_by('-date_paiement')

# API côté Client
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_consulter_paiements_client(request):
    paiements = Paiement.objects.filter(client=request.user).order_by('-date_paiement')
    serializer = PaiementSerializer(paiements, many=True)
    return Response(serializer.data)

# =========================
# API côté Admin
# =========================
@api_view(["GET"])
@permission_classes([IsAdminUser])
def api_gestion_paiements(request):
    paiements = Paiement.objects.all().order_by("-date_paiement")
    serializer = PaiementSerializer(paiements, many=True)
    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAdminUser])
def api_valider_paiement(request, paiement_id):
    paiement = get_object_or_404(Paiement, id=paiement_id)
    paiement.validerPaiement() 
    serializer = PaiementSerializer(paiement)
    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAdminUser])
def api_annuler_paiement(request, paiement_id):
    paiement = get_object_or_404(Paiement, id=paiement_id)
    paiement.annulerPaiement() 
    serializer = PaiementSerializer(paiement)
    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAdminUser])
def api_changer_statut_paiement(request, paiement_id):
    paiement = get_object_or_404(Paiement, id=paiement_id)
    paiement.changerStatutPaiement('CONFIRME')
    serializer = PaiementSerializer(paiement)
    return Response(serializer.data)

# =========================
# Factures
# =========================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_facture_paiement(request, paiement_id):
    paiement = get_object_or_404(Paiement, id=paiement_id)
    commande = paiement.commande
    details = commande.details.all()
    return Response({
        "paiement": PaiementSerializer(paiement).data,
        "commande": commande.id,
        "details": [
            {
                "produit": d.produit.designation,
                "quantite": d.quantite,
                "prix": d.prix_unitaire
            }
            for d in details
        ]
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_facture_paiement_pdf(request, paiement_id):
    paiement = get_object_or_404(Paiement, id=paiement_id, client=request.user)
    commande = paiement.commande
    details = commande.details.all()

    template = get_template("paiements/facture_pdf.html")
    html = template.render({
        "paiement": paiement,
        "commande": commande,
        "details": details,
    })

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="facture-{paiement_id}.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return Response({"error": "Erreur lors de la génération du PDF"}, status=500)

    return response


@api_view(["GET"])
@permission_classes([IsAdminUser])  # ou IsAuthenticated si tu veux que le client voie ses paiements
def api_paiement_detail(request, paiement_id):
    paiement = get_object_or_404(Paiement, id=paiement_id)
    serializer = PaiementSerializer(paiement)
    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAdminUser])
def api_generer_facture(request, paiement_id):
    paiement = get_object_or_404(Paiement, id=paiement_id)
    commande = paiement.commande

    if paiement.statut != "REÇU" or commande.statut != "VALIDEE":
        return Response({"error": "La facture ne peut être générée que si la commande est validée et le paiement reçu."}, status=400)

    if hasattr(paiement, "facture"):
        return Response({"error": "Une facture existe déjà pour ce paiement."}, status=400)

    import uuid
    numero_facture = f"FAC-{uuid.uuid4().hex[:8].upper()}"
    facture = Facture.objects.create(
        commande=commande,
        paiement=paiement,
        numero=numero_facture,
        montant_total=paiement.montant
    )

    serializer = FactureSerializer(facture)
    return Response(serializer.data, status=201)
