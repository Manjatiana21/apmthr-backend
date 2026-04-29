from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import InscriptionClientForm
from django.contrib.auth.decorators import login_required
from .models import Utilisateur
from comptes.models import Role
import re
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from commandes.models import Notification
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate, login


# Create your views here.
def password_is_strong(password):
    if len(password) < 8:
         return False 
    if not re.search(r"[A-Z]", password): 
        return False 
    if not re.search(r"[a-z]", password): 
        return False 
    if not re.search(r"[0-9]", password): 
        return False 
    if not re.search(r"[@$!%*?&]", password): 
        return False 
    return True


def inscription_client(request):
    if request.method == "POST":
        form = InscriptionClientForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.role = "CLIENT"  # rôle fixé automatiquement
            login(request, user)
            return redirect("templates/comptes/espace_client")
    else:
        form = InscriptionClientForm()
    return render(request, "comptes/inscription.html", {"form": form})


def login_view(request):
    # Si déjà connecté
    if request.user.is_authenticated:
        if request.user.role == Role.ADMIN:
            return redirect("tableau_admin")
        else:
            return redirect("espace_client")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.role == Role.ADMIN:
                return redirect("tableau_admin")
            else:
                return redirect("espace_client")
        else:
            messages.error(request, "Identifiants invalides.")
    else:
        form = AuthenticationForm()

    # Page de connexion → pas encore connecté, donc pas de notifications
    return render(request, "comptes/connexion.html", {
        "form": form,
        "notifications": [],
        "nb_notifications_non_lues": 0,
    })




def tableau_de_bord_admin(request):
    if not request.user.est_admin():
        return redirect ('templates/home')
    return render(request, 'comptes/tableau_admin.html')

@login_required(login_url="connexion.html")
def espace_client(request):
    if not request.user.est_client():
        return redirect('home')
    return render(request,'comptes/espace_client.html')

@login_required
def gestion_stocks(request):
    if not request.user.est_admin() or request.user.privilege != 'STOCKS':
        return redirect ('home')
    return render(request, 'stoks/gestion_stocks.html')

@login_required
def gestion_commandes(request):
    if not request.user.est_admin() or request.user.privilege != 'COMMANDES':
        return redirect ('home')
    return render(request, 'commandes/gestion_commandes.html')

@login_required
def gestion_paiements(request):
    if not request.user.est_admin() or request.user.privilege != 'PAIEMENTS':
        return redirect ('home')
    return render(request, 'paiement/')

@login_required 
def tableau_de_bord_global(request):
    if not request.user.est_admin() or request.user.privilege != 'GLOBAL':
        return redirect ('home')
    return render(request, 'stoks/tableau_admin.html"')


@login_required
def mes_notifications(request):
    notifications = request.user.notifications.all().order_by('-id')
    nb_non_lues = notifications.filter(lu=False).count()
    return render(request, "comptes/mes_notifications.html", {
        "notifications": notifications,
        "nb_non_lues": nb_non_lues,
    })

@login_required
def marquer_notification_lue_ajax(request, notif_id):
    notif = Notification.objects.get(id=notif_id, utilisateur=request.user)
    notif.lu = True
    notif.save()
    nb_non_lues = request.user.notifications.filter(lu=False).count()
    return JsonResponse({"success": True, "nb_non_lues": nb_non_lues})

@login_required
def marquer_tout_lu(request):
    request.user.notifications.filter(lu=False).update(lu=True)
    return redirect("mes_notifications")

@login_required
def mes_paiements(request):
    paiements = request.user.paiement_set.all().order_by('-date_paiement')
    return render(request, "comptes/mes_paiements.html", {"paiements": paiements})

@login_required
def gestion_paiements(request):
    if not request.user.est_admin() or request.user.privilege != 'PAIEMENTS':
        return redirect('home')
    paiements = Paiement.objects.all().order_by('-date_paiement')
    return render(request, "admin/gestion_paiements.html", {"paiements": paiements})

@login_required
def notifications_admin(request):
    if request.user.role == "ADMIN":
        notifications = Notification.objects.filter(utilisateur=request.user).order_by("-id")
        nb_non_lues = notifications.filter(lu=False).count()
    else:
        notifications = []
        nb_non_lues = 0   # ✅ valeur par défaut

    return render(request, "comptes/notifications_admin.html", {
        "notifications": notifications,
        "nb_non_lues": nb_non_lues,})

@login_required
def marquer_notif_lue(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, utilisateur=request.user)
    notif.lu = True
    notif.save()
    # Redirection vers la page précédente (admin ou client)
    if request.user.role == "ADMIN":
        return redirect("notifications_admin")
    else:
        return redirect("mes_notifications")

@login_required
def gestion_utilisateurs(request):
    if not request.user.est_admin():
        return redirect('home')
    utilisateurs = Utilisateur.objects.all().order_by('-date_joined')
    return render(request, "comptes/gestion_utilisateurs.html", {"utilisateurs": utilisateurs})


@login_required
def suspendre_utilisateur(request, user_id):
    if not request.user.est_admin():
        return redirect('home')
    utilisateur = get_object_or_404(Utilisateur, id=user_id)
    raison = request.POST.get("raison", "Suspendu par admin")
    utilisateur.is_active = False
    utilisateur.suspension_reason = raison
    utilisateur.save()
    messages.success(request, f"Le compte {utilisateur.username} a été suspendu.")
    return redirect("gestion_utilisateurs")


@login_required
def reactiver_utilisateur(request, user_id):
    if not request.user.est_admin():
        return redirect('home')
    utilisateur = get_object_or_404(Utilisateur, id=user_id)
    utilisateur.is_active = True
    utilisateur.suspension_reason = None
    utilisateur.save()
    messages.success(request, f"Le compte {utilisateur.username} a été réactivé.")
    return redirect("gestion_utilisateurs")

def login_view(request):
    if request.user.is_authenticated:
        if request.user.role == Role.ADMIN:
            return redirect("tableau_admin")
        else:
            return redirect("espace_client")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_active:
                messages.error(request, "Votre compte est suspendu. Veuillez contacter l’administrateur.")
                return redirect("authentification")   # ✅ à l'intérieur de la fonction

            # ✅ Connexion autorisée uniquement si actif
            login(request, user)
            if user.role == Role.ADMIN:
                return redirect("tableau_admin")
            else:
                return redirect("espace_client")
        else:
            messages.error(request, "Identifiants invalides.")
    else:
        form = AuthenticationForm()

    return render(request, "connexion")
