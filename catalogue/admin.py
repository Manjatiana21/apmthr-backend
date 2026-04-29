from django.contrib import admin
from .models import TypeProduit, Fournisseur, Produit

# Register your models here.
@admin.register(TypeProduit)
class TypeProduitAdmin(admin.ModelAdmin):
    list_display = ('libelleTP',)
    search_fields = ('libelleTP',)

@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'contact', 'type_F')
    search_fields = ('nom', 'contact')

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('designation', 'stock', 'type_produit', 'fournisseur')
    search_fields = ('designation',)
    list_filter = ('type_produit', 'fournisseur')

