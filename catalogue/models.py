from django.db import models
from stocks.models import MouvementStock
from django.utils.timezone import now


# Create your models here.
class TypeProduit(models.Model):
    libelleTP = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.libelleTP
        
    def ajouterTypeProduit(self, libelle):
        self.libelleTP = libelle
        self.save()
        
    def modifierTypeProduit(self, libelle):
        self.libelleTP = libelle
        self.save()
        
    def supprimerTypeProduit(self):
        self.delete()
        
    def listerProduitsParType(self):
        return self.produits.all()
        
    def compterProduitsParType(self):
        return self.produits.count()
        
    def filtrerProduitsDisponibles(self):
        return self.produits.filter(stock__gt=0)


class Fournisseur(models.Model):
    nom = models.CharField(max_length=150)
    contact = models.CharField(max_length=100, blank=True)
    type_F = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.nom
        
    def consulterProduitsFourn(self):
        return self.produits.all()
        
    def ajouterFournisseur(self, nom, contact, type_F):
        self.nom = nom
        self.contact = contact
        self.type_F = type_F
        self.save()
        
    def modifierFournisseur(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        self.save()
        
    @classmethod
    def filtrerParTypeFournisseur(cls, type_F):
        return cls.objects.filter(type_F=type_F)


class Produit(models.Model):
    designation = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    stock = models.IntegerField(default=0)
    type_produit = models.ForeignKey(TypeProduit, on_delete=models.CASCADE, related_name='produits')
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE, related_name='produits')
    prix = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    image = models.ImageField(upload_to="produits/", null=True, blank=True)
    date_ajout = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return f"{self.designation} - {self.prix} Ar"

    def __str__(self): 
        return self.designation
    

    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Vérifie si c'est un nouveau produit
        super().save(*args, **kwargs)

        if is_new and self.stock > 0:
            # ✅ Mouvement ENTREE automatique à la création du produit
            MouvementStock.objects.create(
                produit=self,
                quantite=self.stock,
                type_mouvement="ENTREE",
                
            )

    def retirer_stock(self, quantite):
        """Décrémenter le stock après une commande."""
        self.stock -= quantite
        if self.stock <= 0:
            self.stock = 0
            # Optionnel : ajouter un champ is_epuise = True
        self.save()

    def ajouter_stock(self, quantite):
        """Incrémenter le stock après réception fournisseur."""
        self.stock += quantite
        self.save()
        MouvementStock.objects.create( 
            produit=self, 
            quantite=quantite, 
            type_mouvement="ENTREE", 
            utilisateur=utilisateur )

    @property
    def est_epuise(self):
        return self.stock <= 0


    def retirer_stock(self, quantite, utilisateur=None):
        self.stock -= quantite
        if self.stock < 0:
            self.stock = 0
        self.save()
        MouvementStock.objects.create(
            produit=self,
            quantite=quantite,
            type_mouvement="SORTIE",
            utilisateur=utilisateur
        )


        
    def ajouterProduit(self, designation, description, stock, type_produit, fournisseur,prix, image=None):
        self.designation = designation
        self.description = description
        self.stock = stock
        self.type_produit = type_produit
        self.fournisseur = fournisseur
        self.prix=prix
        if image: 
            self.image = image
        self.save()
        
    def modifierProduit(self, **kwargs):
        for attr, value in kwargs.items():
            if hasattr(self,attr):
                setattr(self, attr, value)
        self.save()
        return self
        
    def supprimerProduit(self):
        self.delete()
        
    def consulterStock(self):
        return self.stock
        
    def calculerStockCritique(self, seuil=5):
        return self.stock <= seuil
        
    def afficherProduitsSimilaires(self):
        return Produit.objects.filter(type_produit=self.type_produit).exclude(id=self.id)

