from django.db import models
from comptes.models import Utilisateur, Notification
from django.utils import timezone
from datetime import timedelta

class Livraison(models.Model):
    STATUT_CHOICES = [
        ("NON_DEMARREE", "NON_DEMARRE"),
        ("EN_COURS", "EN_COURS"),
        ("LIVREE", "LIVREE"),
    ]

    commande = models.ForeignKey(
        "commandes.Commande",
        on_delete=models.CASCADE,
        related_name="livraison"
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="NON_DEMARREE"
    )
    date_prevue = models.DateTimeField(blank=True, null=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Livraison commande #{self.commande.id} - {self.statut}"

    def demarrer(self):
        self.statut = "EN_COURS"
        self.save()
        Notification.objects.create(
            utilisateur=self.commande.client,
            message="Votre commande est en cours de livraison."
        )

    def terminer(self):
        self.statut = "LIVREE"
        self.save()
        Notification.objects.create(
            utilisateur=self.commande.client,
            message="Votre commande a été livrée. Merci pour votre confiance !"
        )

    def planifier(self, delai_heures=48):
        self.date_prevue = timezone.now() + timedelta(hours=delai_heures)
        self.statut = "EN_COURS"
        self.save()
        produits = ", ".join([
            f"{d.produit.designation} x{d.quantite}"
            for d in self.commande.details.all()
        ])
        Notification.objects.create(
            utilisateur=self.commande.client,
            message=f"Votre commande ({produits}) sera livrée à partir du {self.date_prevue.strftime('%d/%m/%Y %H:%M')}."
        )
