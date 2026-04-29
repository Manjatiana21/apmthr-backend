from django import forms
from .models import Utilisateur
import re



class InscriptionClientForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput,
        required=True
    )
    password2 = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput,
        required=True
    )

    class Meta:
        model = Utilisateur
        fields = ["username", "email", "adresse","telephone"]

    def clean_password1(self): 
        password1 = self.cleaned_data.get("password1")

        if len(password1) < 8:
            raise forms.ValidationError("Le mot de passe doit contenir au moins 8 caractères.")
        if not re.search(r"[A-Z]", password1):
            raise forms.ValidationError("Le mot de passe doit contenir au moins une majuscule.")
        if not re.search(r"[a-z]", password1):
            raise forms.ValidationError("Le mot de passe doit contenir au moins une minuscule.")
        if not re.search(r"[0-9]", password1):
            raise forms.ValidationError("Le mot de passe doit contenir au moins un chiffre.")
        if not re.search(r"[@$!%*?&]", password1):
            raise forms.ValidationError("Le mot de passe doit contenir au moins un caractère spécial (@$!%*?&).")

        return password1

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])  
        user.role = "CLIENT"
        if commit:
            user.save()
        return user