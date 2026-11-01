from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Entry


class EntryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alice", password="pass12345")
        self.other = User.objects.create_user("bob", password="pass12345")
        self.entry = Entry.objects.create(author=self.user, title="Первая", content="Текст про море")

    def test_list_requires_login(self):
        response = self.client.get(reverse("entries:list"))
        self.assertEqual(response.status_code, 302)

    def test_user_sees_only_own_entries(self):
        Entry.objects.create(author=self.other, title="Чужая", content="секрет")
        self.client.login(username="alice", password="pass12345")
        response = self.client.get(reverse("entries:list"))
        self.assertContains(response, "Первая")
        self.assertNotContains(response, "Чужая")

    def test_foreign_entry_returns_404(self):
        self.client.login(username="bob", password="pass12345")
        response = self.client.get(reverse("entries:detail", args=[self.entry.pk]))
        self.assertEqual(response.status_code, 404)

    def test_search_by_content(self):
        self.client.login(username="alice", password="pass12345")
        response = self.client.get(reverse("entries:list"), {"q": "море"})
        self.assertContains(response, "Первая")
