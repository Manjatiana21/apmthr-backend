from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager

# Create your models here.
class Role(models.TextChoices):
    CLIENT = "CLIENT", "Client" 
    ADMIN = "ADMIN", "Admin" 
    

class Privilege(models.TextChoices):
    STOCKS = 'STOCKS', 'Gestion des stocks'
    COMMANDES = 'COMMANDES', 'Supervision des commandes'
    PAIEMENTS = 'PAIEMENTS', 'Validation des paiements'
    GLOBAL = 'GLOBAL', 'Supervision générale'
    
class Utilisateur(AbstractUser):
    adresse = models.CharField(max_length=255, blank=True, null=True) 
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.CLIENT)
    email = models.EmailField(blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    privilege = models.CharField(max_length=20,choices=Privilege.choices, blank=True, null=True)

    is_active = models.BooleanField(default=True)  # déjà géré par AbstractUser
    suspension_reason = models.TextField(blank=True, null=True)  # raison suspension
    
    USERNAME_FIELD = "username"
    
    def est_admin(self):
        return self.role == Role.ADMIN

    def est_client(self):
        return self.role == Role.CLIENT 
    
    def __str__(self): 
        return f"{self.username} ({self.role})"

    def seConnecter(self, request):
        from django.contrib.auth import login
        login(request, self)
    
    def seDeconnecter(self, request):
        from django.contrib.auth import logout
        logout(request)
    
    def modifierProfil(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        self.save()
    
    def consulterHistorique(self):
        return self.commandes.all()

class Notification(models.Model):
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    message = models.TextField()
    lu = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    lien = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.utilisateur.username} - {'LU' if self.lu else 'NON LU'}"


    def modifierProfil(self, **kwargs):
        """Mettre à jour le profil utilisateur."""
        for field, value in kwargs.items():
            if hasattr(self, field) and value is not None:
                setattr(self, field, value)
        self.save()
        return self