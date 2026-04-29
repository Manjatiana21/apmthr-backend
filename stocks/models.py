from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class MouvementStock(models.Model):
    TYPE_CHOICES = [
        ("ENTREE", "Entrée"),
        ("SORTIE", "Sortie"),
    ]

    produit = models.ForeignKey("catalogue.Produit", on_delete=models.CASCADE, related_name="mouvements")
    quantite = models.PositiveIntegerField()
    commande = models.ForeignKey("commandes.Commande", on_delete=models.SET_NULL, null=True, blank=True)
    type_mouvement = models.CharField(max_length=10, choices=TYPE_CHOICES)
    date_mouvement = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type_mouvement} - {self.produit.designation} ({self.quantite})"
