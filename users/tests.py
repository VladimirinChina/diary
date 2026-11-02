from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class UserTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user("alice", password="pass12345")

    def test_register_page_opens(self) -> None:
        response = self.client.get(reverse("users:register"))
        self.assertEqual(response.status_code, 200)

    def test_register_success(self) -> None:
        response = self.client.post(
            reverse("users:register"),
            {
                "username": "newuser",
                "email": "new@example.com",
                "password1": "StrongPass12345!",
                "password2": "StrongPass12345!",
            },
        )
        self.assertRedirects(response, reverse("entries:list"))
        self.assertTrue(User.objects.filter(username="newuser").exists())
        self.assertIn("_auth_user_id", self.client.session)

    def test_register_with_password_mismatch(self) -> None:
        response = self.client.post(
            reverse("users:register"),
            {
                "username": "newuser",
                "email": "new@example.com",
                "password1": "StrongPass12345!",
                "password2": "AnotherPass12345!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="newuser").exists())

    def test_login_success(self) -> None:
        response = self.client.post(
            reverse("users:login"),
            {"username": "alice", "password": "pass12345"},
        )
        self.assertRedirects(response, reverse("entries:list"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_with_wrong_password(self) -> None:
        response = self.client.post(
            reverse("users:login"),
            {"username": "alice", "password": "wrong-password"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout(self) -> None:
        self.client.login(username="alice", password="pass12345")
        response = self.client.post(reverse("users:logout"))
        self.assertRedirects(response, reverse("users:login"))
        self.assertNotIn("_auth_user_id", self.client.session)
