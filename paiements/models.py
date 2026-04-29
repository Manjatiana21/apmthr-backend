from django.db import models
from django.conf import settings
from comptes.models import Notification
from django.utils import timezone


class ModePaiement(models.Model):
    mode_paiement = models.CharField(max_length=50, unique=True)
    numero_admin = models.CharField(max_length=20, null=True, blank=True)
    
    def __str__(self):
        return self.mode_paiement

class Paiement(models.Model):
    commande = models.ForeignKey("commandes.Commande", on_delete=models.CASCADE, related_name="paiements")
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    mode_paiement = models.ForeignKey("paiements.ModePaiement", on_delete=models.SET_NULL, null=True, blank=True)
    montant = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    statut = models.CharField(max_length=50, default="EN_ATTENTE", choices=[
        ("EN_ATTENTE", "En_attente"),
        ("REÇU", "Reçu"),
        ("ANNULE", "Annulé"),
    ])
    date_paiement = models.DateTimeField(blank=True, null=True)
    preuve = models.FileField(upload_to="preuves/", null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.commande and (self.montant == 0 or self.montant is None):
            self.montant = self.commande.total
        if self.commande and (self.mode_paiement is None):
            self.mode_paiement = self.commande.mode_paiement
        super().save(*args, **kwargs)

    def validerPaiement(self):
        """Valider le paiement (statut = REÇU)."""
        self.statut = "REÇU"
        self.date_paiement = timezone.now()
        self.save()

    def annulerPaiement(self):
        """Annuler le paiement (statut = ANNULE)."""
        self.statut = "ANNULE"
        self.save()

    def __str__(self):
        return f"Paiement {self.id} - Commande {self.commande.id} - {self.client.username} - {self.statut}"
