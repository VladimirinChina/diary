from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Entry, Mood


class EntryTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user("alice", password="pass12345")
        self.other = User.objects.create_user("bob", password="pass12345")
        self.entry = Entry.objects.create(
            author=self.user, title="Первая", content="Текст про море"
        )

    def login_alice(self) -> None:
        self.client.login(username="alice", password="pass12345")

    def create_entries(self, count: int) -> None:
        for number in range(count):
            Entry.objects.create(
                author=self.user, title=f"Запись {number}", content="текст"
            )

    # --- доступ и приватность ---

    def test_list_requires_login(self) -> None:
        response = self.client.get(reverse("entries:list"))
        self.assertEqual(response.status_code, 302)

    def test_user_sees_only_own_entries(self) -> None:
        Entry.objects.create(author=self.other, title="Чужая", content="секрет")
        self.login_alice()
        response = self.client.get(reverse("entries:list"))
        self.assertContains(response, "Первая")
        self.assertNotContains(response, "Чужая")

    def test_foreign_entry_returns_404(self) -> None:
        self.client.login(username="bob", password="pass12345")
        response = self.client.get(reverse("entries:detail", args=[self.entry.pk]))
        self.assertEqual(response.status_code, 404)

    def test_create_redirects_anonymous(self) -> None:
        url = reverse("entries:create")
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('users:login')}?next={url}")

    def test_update_redirects_anonymous(self) -> None:
        url = reverse("entries:update", args=[self.entry.pk])
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('users:login')}?next={url}")

    def test_delete_redirects_anonymous(self) -> None:
        url = reverse("entries:delete", args=[self.entry.pk])
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('users:login')}?next={url}")

    def test_foreign_entry_cannot_be_updated(self) -> None:
        self.client.login(username="bob", password="pass12345")
        response = self.client.post(
            reverse("entries:update", args=[self.entry.pk]),
            {"title": "Взлом", "mood": Mood.GOOD, "content": "чужой текст"},
        )
        self.assertEqual(response.status_code, 404)
        self.entry.refresh_from_db()
        self.assertEqual(self.entry.title, "Первая")

    def test_foreign_entry_cannot_be_deleted(self) -> None:
        self.client.login(username="bob", password="pass12345")
        response = self.client.post(reverse("entries:delete", args=[self.entry.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Entry.objects.filter(pk=self.entry.pk).exists())

    # --- создание, редактирование, удаление ---

    def test_create_entry_sets_author(self) -> None:
        self.login_alice()
        response = self.client.post(
            reverse("entries:create"),
            {"title": "Новая", "mood": Mood.GOOD, "content": "Текст новой записи"},
        )
        entry = Entry.objects.get(title="Новая")
        self.assertRedirects(response, entry.get_absolute_url())
        self.assertEqual(entry.author, self.user)
        self.assertEqual(entry.mood, Mood.GOOD)

    def test_create_entry_with_empty_title_is_invalid(self) -> None:
        self.login_alice()
        response = self.client.post(
            reverse("entries:create"),
            {"title": "", "mood": Mood.GOOD, "content": "Текст"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Entry.objects.filter(author=self.user).count(), 1)

    def test_update_own_entry(self) -> None:
        self.login_alice()
        response = self.client.post(
            reverse("entries:update", args=[self.entry.pk]),
            {"title": "Изменённая", "mood": Mood.SAD, "content": "Новый текст"},
        )
        self.assertRedirects(response, self.entry.get_absolute_url())
        self.entry.refresh_from_db()
        self.assertEqual(self.entry.title, "Изменённая")
        self.assertEqual(self.entry.mood, Mood.SAD)

    def test_delete_own_entry(self) -> None:
        self.login_alice()
        response = self.client.post(reverse("entries:delete", args=[self.entry.pk]))
        self.assertRedirects(response, reverse("entries:list"))
        self.assertFalse(Entry.objects.filter(pk=self.entry.pk).exists())

    # --- поиск и фильтры ---

    def test_search_by_content(self) -> None:
        self.login_alice()
        response = self.client.get(reverse("entries:list"), {"q": "море"})
        self.assertContains(response, "Первая")

    def test_search_by_title(self) -> None:
        Entry.objects.create(
            author=self.user, title="Уникальный заголовок", content="другое"
        )
        self.login_alice()
        response = self.client.get(reverse("entries:list"), {"q": "Уникальный"})
        self.assertContains(response, "Уникальный заголовок")
        self.assertNotContains(response, "Первая")

    def test_search_without_results(self) -> None:
        self.login_alice()
        response = self.client.get(reverse("entries:list"), {"q": "несуществующее"})
        self.assertContains(response, "ничего не найдено")

    def test_default_mood_is_neutral(self) -> None:
        self.assertEqual(self.entry.mood, Mood.NEUTRAL)

    def test_filter_by_mood(self) -> None:
        Entry.objects.create(
            author=self.user, title="Грустная", content="дождь", mood=Mood.SAD
        )
        self.login_alice()
        response = self.client.get(reverse("entries:list"), {"mood": Mood.SAD})
        self.assertContains(response, "Грустная")
        self.assertNotContains(response, "Первая")

    def test_filter_by_each_mood(self) -> None:
        for mood in Mood.values:
            Entry.objects.create(
                author=self.user, title=f"Запись {mood}", content="текст", mood=mood
            )
        self.login_alice()
        for mood in Mood.values:
            with self.subTest(mood=mood):
                response = self.client.get(reverse("entries:list"), {"mood": mood})
                entries = response.context["entries"]
                self.assertGreater(len(entries), 0)
                self.assertTrue(all(entry.mood == mood for entry in entries))

    def test_invalid_mood_filter_is_ignored(self) -> None:
        self.login_alice()
        response = self.client.get(reverse("entries:list"), {"mood": "unknown"})
        total = Entry.objects.filter(author=self.user).count()
        self.assertEqual(len(response.context["entries"]), total)

    # --- пагинация и модель ---

    def test_pagination_first_page(self) -> None:
        self.create_entries(11)
        self.login_alice()
        response = self.client.get(reverse("entries:list"))
        self.assertEqual(len(response.context["entries"]), 9)
        self.assertTrue(response.context["is_paginated"])

    def test_pagination_second_page(self) -> None:
        self.create_entries(11)
        self.login_alice()
        response = self.client.get(reverse("entries:list"), {"page": 2})
        self.assertEqual(len(response.context["entries"]), 3)

    def test_get_absolute_url(self) -> None:
        self.assertEqual(
            self.entry.get_absolute_url(),
            reverse("entries:detail", args=[self.entry.pk]),
        )

    def test_str_returns_title(self) -> None:
        self.assertEqual(str(self.entry), "Первая")
