from rest_framework import viewsets
from .models import Utilisateur, Notification
from django.shortcuts import get_object_or_404
from .serializers import (UtilisateurSerializer, NotificationSerializer,PaiementSerializer, InscriptionSerializer,ModifierProfilSerializer)
from rest_framework.decorators import api_view,  permission_classes
from rest_framework.response import Response
from django.utils.timezone import now
from django.db.models import Count, Sum
from catalogue.models import Produit
from commandes.models import Commande, Details
from paiements.models import Paiement
from livraisons.models import Livraison
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.contrib.auth import authenticate, login
from commandes.models import Notification
from paiements.models import Paiement
from rest_framework import status
from .serializers import InscriptionSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import logout
from datetime import datetime
from django.db.models.functions import ExtractMonth, ExtractYear
from rest_framework.views import APIView
from django.contrib.auth.hashers import check_password

User = get_user_model()

@api_view(["GET"])
@permission_classes([IsAdminUser])
def api_admin_stats(request):
    current_year = datetime.now().year
    today = now().date()

    # ✅ Commandes
    commandes_validees = Commande.objects.filter(statut="VALIDEE").count()
    commandes_attente = Commande.objects.filter(statut="EN_ATTENTE").count()
    commandes_annulees = Commande.objects.filter(statut="ANNULEE").count()

    # ✅ Ventes par mois (uniquement commandes validées de l’année en cours)
    ventes_par_mois_qs = (
        Commande.objects.filter(statut="VALIDEE", date_commande__year=current_year)
        .annotate(mois=ExtractMonth("date_commande"))
        .values("mois")
        .annotate(total=Count("id"))
        .order_by("mois")
    )

    ventes_par_mois = [0] * 12
    for item in ventes_par_mois_qs:
        ventes_par_mois[item["mois"] - 1] = item["total"]

    # ✅ Produits vendus (Top 5)
    produits_vendus_qs = (
        Details.objects.filter(
            commande__statut="VALIDEE",
            commande__paiements__statut="REÇU"  # ⚠️ uniformiser aussi les statuts Paiement
        )
        .values("produit__designation")
        .annotate(total_vendu=Sum("quantite"))
        .order_by("-total_vendu")
    )

    # ✅ Paiements
    paiements_recus = Paiement.objects.filter(statut="REÇU").count()
    paiements_attente = Paiement.objects.filter(statut="EN_ATTENTE").count()

    # ✅ Livraisons
    livraisons_en_cours = Livraison.objects.filter(statut="EN_COURS").count()
    livraisons_livrees = Livraison.objects.filter(statut="LIVREE").count()

    clients_today = User.objects.filter(date_joined__date=today).count()
    clients_total = User.objects.count()

    return Response({
        "commandes_validees": commandes_validees,
        "commandes_attente": commandes_attente,
        "commandes_annulees": commandes_annulees,
        "paiements_recus": paiements_recus,
        "paiements_attente": paiements_attente,
        "livraisons_en_cours": livraisons_en_cours,
        "livraisons_livrees": livraisons_livrees,
        "annee": current_year,
        "ventes_par_mois": ventes_par_mois,
        "produits_vendus": list(produits_vendus_qs[:5]),
        "clients_today": clients_today,
        "clients_total": clients_total,
    })

@api_view(["GET"])
@permission_classes([IsAdminUser])
def api_utilisateurs(request):
    utilisateurs = Utilisateur.objects.all().order_by("-date_joined")
    serializer = UtilisateurSerializer(utilisateurs, many=True)
    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAdminUser])
def api_suspendre_utilisateur(request, user_id):
    utilisateur = get_object_or_404(Utilisateur, id=user_id)
    raison = request.data.get("raison", "Suspendu par admin")
    utilisateur.is_active = False
    utilisateur.suspension_reason = raison
    utilisateur.save()
    return Response({"status": "compte suspendu", "raison": utilisateur.suspension_reason})

@api_view(["POST"])
@permission_classes([IsAdminUser])
def api_reactiver_utilisateur(request, user_id):
    utilisateur = get_object_or_404(Utilisateur, id=user_id)
    utilisateur.is_active = True
    utilisateur.suspension_reason = None
    utilisateur.save()
    return Response({"status": "compte réactivé"})
    

class UtilisateurViewSet(viewsets.ModelViewSet):
    queryset = Utilisateur.objects.all().order_by('username')
    serializer_class = UtilisateurSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all().order_by('-date_creation')
    serializer_class = NotificationSerializer



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_logout(request):
    logout(request)
    return Response({"success": True, "message": "Déconnexion réussie"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_mes_notifications(request):
    notifications = request.user.notifications.all().order_by("-id")
    serializer = NotificationSerializer(notifications, many=True)
    nb_non_lues = notifications.filter(lu=False).count()
    return Response({"notifications": serializer.data, "nb_non_lues": nb_non_lues})

@api_view(["GET"])
@permission_classes([IsAdminUser])
def api_notifications_admin(request):
    notifications = Notification.objects.filter(utilisateur=request.user).order_by("-id")
    serializer = NotificationSerializer(notifications, many=True)
    nb_non_lues = notifications.filter(lu=False).count()
    return Response({"notifications": serializer.data, "nb_non_lues": nb_non_lues})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_marquer_notif_lue(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, utilisateur=request.user)
    notif.lu = True
    notif.save()
    nb_non_lues = request.user.notifications.filter(lu=False).count()
    return Response({"success": True, "nb_non_lues": nb_non_lues})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_marquer_tout_lu(request):
    request.user.notifications.filter(lu=False).update(lu=True)
    return Response({"success": True})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_mes_paiements(request):
    paiements = request.user.paiement_set.all().order_by('-date_paiement')
    serializer = PaiementSerializer(paiements, many=True)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAdminUser])
def api_gestion_paiements(request):
    paiements = Paiement.objects.all().order_by('-date_paiement')
    serializer = PaiementSerializer(paiements, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user is not None:
        if not user.is_active:
            return Response({'error': 'Votre compte est suspendu. Veuillez contacter l’administrateur.'}, status=403)
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'role': user.role
        })
    else:
        return Response({'error': 'Identifiants invalides'}, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = InscriptionSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            "message": "Inscription réussie",
            "username": user.username,
            "role": user.role
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_view(request):
    user = request.user
    serializer = UtilisateurSerializer(user)
    return Response(serializer.data)

# 🔹 Modifier le nom
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def modifier_nom(request):
    user = request.user
    new_name = request.data.get("username")
    if not new_name:
        return Response({"detail": "Nom requis."}, status=status.HTTP_400_BAD_REQUEST)
    user.username = new_name
    user.save()
    return Response({"detail": "Nom modifié avec succès."}, status=status.HTTP_200_OK)


# 🔹 Modifier le téléphone
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def modifier_telephone(request):
    user = request.user
    new_tel = request.data.get("telephone")
    if not new_tel:
        return Response({"detail": "Téléphone requis."}, status=status.HTTP_400_BAD_REQUEST)
    user.telephone = new_tel
    user.save()
    return Response({"detail": "Téléphone modifié avec succès."}, status=status.HTTP_200_OK)


# 🔹 Modifier l’adresse
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def modifier_adresse(request):
    user = request.user
    new_adresse = request.data.get("adresse")
    if not new_adresse:
        return Response({"detail": "Adresse requise."}, status=status.HTTP_400_BAD_REQUEST)
    user.adresse = new_adresse
    user.save()
    return Response({"detail": "Adresse modifiée avec succès."}, status=status.HTTP_200_OK)


# 🔹 Modifier l’email
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def modifier_email(request):
    user = request.user
    new_email = request.data.get("email")
    if not new_email:
        return Response({"detail": "Email requis."}, status=status.HTTP_400_BAD_REQUEST)
    user.email = new_email
    user.save()
    return Response({"detail": "Email modifié avec succès."}, status=status.HTTP_200_OK)


# 🔹 Modifier le mot de passe
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def modifier_motdepasse(request):
    user = request.user
    old_password = request.data.get("old_password")
    new_password = request.data.get("new_password")

    if not old_password or not new_password:
        return Response({"detail": "Ancien et nouveau mot de passe requis."}, status=status.HTTP_400_BAD_REQUEST)

    if not check_password(old_password, user.password):
        return Response({"detail": "Ancien mot de passe incorrect."}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()
    return Response({"detail": "Mot de passe modifié avec succès."}, status=status.HTTP_200_OK)
