from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from comptes.models import Role

Utilisateur = get_user_model()

class LoginRedirectTests(TestCase):

    def setUp(self):
        # Création d'un client
        self.client_user = Utilisateur.objects.create_user(
            username="client1",
            password="test123",
            role=Role.CLIENT
        )
        # Création d'un admin
        self.admin_user = Utilisateur.objects.create_user(
            username="admin1",
            password="test123",
            role=Role.ADMIN
        )

    def test_client_redirection(self):
        """Un client doit être redirigé vers espace_client"""
        response = self.client.post(reverse("authentification"), {
            "username": "client1",
            "password": "test123"
        })
        self.assertRedirects(response, reverse("espace_client"))

    def test_admin_redirection(self):
        """Un admin doit être redirigé vers dashboard_admin"""
        response = self.client.post(reverse("authentification"), {
            "username": "admin1",
            "password": "test123"
        })
        self.assertRedirects(response, reverse("tableau_admin"))
