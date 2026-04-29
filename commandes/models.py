from django.db import models
from catalogue.models import Produit
from comptes.models import Utilisateur, Notification
from stocks.models import MouvementStock
from django.conf import settings
from django.contrib.auth import get_user_model
from livraisons.models import Livraison
from django.db.models.signals import post_save
from django.dispatch import receiver


STATUTS = [ ("EN_ATTENTE", "En attente"), ("VALIDEE", "Validée"), ("ANNULEE", "Annulée"), ]

class Commande(models.Model):
    client = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="commandes")
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, null=True, blank=True)
    quantite = models.PositiveIntegerField(default=1)
    date_commande = models.DateTimeField(auto_now_add=True)
    mode_paiement = models.ForeignKey("paiements.ModePaiement", on_delete=models.SET_NULL, null=True)
    adresse_livraison = models.CharField(max_length=255, null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default="EN_ATTENTE") 
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self): 
        return f"Commande #{self.id} - {self.client.username}"

    def calculerTotal(self):
        total = sum(detail.sous_total for detail in self.details.all())
        self.total = total
        self.save()
        return total

    def creerCommande(self): 
        """
        Crée une commande et notifie client + admin.
        Vérifie aussi le stock et notifie l'admin si insuffisant.
        """
        details = self.details.all()
        produits = ", ".join([f"{d.quantite} x {d.produit.designation}" for d in details]) if details.exists() else "aucun produit"

        # ✅ notification client
        Notification.objects.create(
            utilisateur=self.client,
            message=f"Votre commande ({produits}) a été enregistrée."
        )

        # ✅ notification admin (nouvelle commande)
        admins = Utilisateur.objects.filter(role="ADMIN")
        for admin in admins:
            Notification.objects.create(
                utilisateur=admin,
                message=f"Nouvelle commande de {self.client.username} : {produits}"
            )

        # ✅ vérification du stock
        for d in details:
            if d.quantite > d.produit.stock:   # suppose que Produit a un champ stock
                for admin in admins:
                    Notification.objects.create(
                        utilisateur=admin,
                        message=f"⚠️ Stock insuffisant pour {d.produit.designation} (commande de {self.client.username}, demandé {d.quantite}, disponible {d.produit.stock}). Veuillez vérifier et annuler/valider manuellement."
                    )
                # ❌ ne pas annuler automatiquement
                self.statut = "EN_ATTENTE"
                self.save()
                break


    def validerCommande(self):
        self.statut = "VALIDEE"
        self.save()

        details = self.details.all()
        produits = ", ".join([f"{d.quantite} x {d.produit.designation}" for d in details]) if details.exists() else "aucun produit"

        # ✅ notification client
        Notification.objects.create(
            utilisateur=self.client,
            message=f"Votre commande ({produits}) a été validée. Merci pour votre confiance !"
        )

        # ✅ notification admin
        admins = Utilisateur.objects.filter(role="ADMIN")
        for admin in admins:
            Notification.objects.create(
                utilisateur=admin,
                message=f"Commande validée pour {self.client.username} : {produits}"
            )


    def annulerCommande(self, par_client=False):
        self.statut = "ANNULEE"
        self.save()

        details = self.details.all()
        produits = ", ".join([f"{d.quantite} x {d.produit.designation}" for d in details]) if details.exists() else "aucun produit"

        # ✅ notification client
        if par_client:
            message_client = f"Votre commande ({produits}) a été annulée par vous-même."
        else:
            message_client = f"Votre commande ({produits}) a été annulée par l’admin."
        Notification.objects.create(utilisateur=self.client, message=message_client)

        # ✅ notification admin
        admins = Utilisateur.objects.filter(role="ADMIN")
        for admin in admins:
            if par_client:
                message_admin = f"{self.client.username} a annulé sa commande : {produits}"
            else:
                message_admin = f"Commande annulée par l’admin pour {self.client.username} : {produits}"
            Notification.objects.create(utilisateur=admin, message=message_admin)

        def changerStatut(self, nouveau_statut):
            self.statut = nouveau_statut
        self.save()

    def consulterCommande(self):
        return {
            "id": self.id,
            "client": self.client.username,
            "statut": self.statut,
            "total": self.total,
            "date": self.date_commande
        }

    def __str__(self):
        return f"Commande {self.id} - {self.client.username}"

class Details(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name="details")
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT)  # ✅ pas de related_name ici
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=2)
    sous_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self): 
        return f"{self.produit.designation} x {self.quantite}"

    def save(self, *args, **kwargs):
        self.sous_total = self.quantite * self.prix_unitaire
        super().save(*args, **kwargs)

    def ajouterDetails(self, commande, produit, quantite, prix_unitaire):
        self.commande = commande
        self.produit = produit
        self.quantite = quantite
        self.prix_unitaire = prix_unitaire
        self.calculerSousTotal()
        self.save()

    def modifierDetails(self, quantite=None, prix_unitaire=None):
        if quantite:
            self.quantite = quantite
        if prix_unitaire:
            self.prix_unitaire = prix_unitaire
        self.calculerSousTotal()
        self.save()

    def supprimerDetails(self):
        self.delete()

    def calculerSousTotal(self):
        self.sous_total = self.quantite * self.prix_unitaire

    def __str__(self):
        return f"Détails #{self.id} - {self.produit}"

@receiver(post_save, sender=Commande)
def creer_livraison_automatique(sender, instance, created, **kwargs):
    if instance.statut == "VALIDEE":
        Livraison.objects.get_or_create(
            commande=instance,
            defaults={"statut": "NON_DEMARREE"}
        )



class CommandeItem(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name="items")
    produit = models.ForeignKey("catalogue.Produit", on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
