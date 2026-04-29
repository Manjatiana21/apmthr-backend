from django.db import models
from commandes.models import Commande
from paiements.models import Paiement

class Facture(models.Model):
    commande = models.OneToOneField(Commande, on_delete=models.CASCADE, related_name="facture")
    paiement = models.ForeignKey(Paiement, on_delete=models.CASCADE, related_name="factures")
    numero = models.CharField(max_length=50, unique=True)
    date_emission = models.DateTimeField(auto_now_add=True)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    envoyee = models.BooleanField(default=False)

    def __str__(self):
        return f"Facture {self.numero} - Commande {self.commande.id}"
