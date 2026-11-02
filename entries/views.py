from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q, QuerySet
from django.forms import ModelForm
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import EntryForm
from .models import Entry, Mood


class OwnerQuerysetMixin(LoginRequiredMixin):
    """Ограничивает выборку записями текущего пользователя."""

    request: HttpRequest

    def get_queryset(self) -> QuerySet[Entry]:
        user = self.request.user
        assert user.is_authenticated
        return Entry.objects.filter(author=user)


class EntryListView(OwnerQuerysetMixin, ListView):
    """Список записей текущего пользователя с поиском и фильтром по настроению."""
    model = Entry
    template_name = "entries/entry_list.html"
    context_object_name = "entries"
    paginate_by = 9

    def get_queryset(self) -> QuerySet[Entry]:
        queryset = super().get_queryset()
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            )
        mood = self.request.GET.get("mood", "")
        if mood in Mood.values:
            queryset = queryset.filter(mood=mood)
        return queryset

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        context["mood"] = self.request.GET.get("mood", "")
        context["moods"] = Mood.choices
        return context


class EntryDetailView(OwnerQuerysetMixin, DetailView):
    """Подробный просмотр одной записи, доступный только её автору."""
    model = Entry
    template_name = "entries/entry_detail.html"


class EntryCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Создание записи: автором автоматически становится текущий пользователь."""
    model = Entry
    form_class = EntryForm
    template_name = "entries/entry_form.html"
    success_message = "Запись создана"

    def form_valid(self, form: "ModelForm[Any]") -> HttpResponse:
        form.instance.author = self.request.user
        return super().form_valid(form)


class EntryUpdateView(OwnerQuerysetMixin, SuccessMessageMixin, UpdateView):
    """Редактирование записи, доступное только её автору."""
    model = Entry
    form_class = EntryForm
    template_name = "entries/entry_form.html"
    success_message = "Запись обновлена"


class EntryDeleteView(OwnerQuerysetMixin, DeleteView):
    """Удаление записи с подтверждением, доступное только её автору."""
    model = Entry
    template_name = "entries/entry_confirm_delete.html"
    success_url = reverse_lazy("entries:list")
