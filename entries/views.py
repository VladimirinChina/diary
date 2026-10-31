from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import EntryForm
from .models import Entry


class OwnerQuerysetMixin(LoginRequiredMixin):
    """Ограничивает выборку записями текущего пользователя."""

    def get_queryset(self):
        return Entry.objects.filter(author=self.request.user)


class EntryListView(OwnerQuerysetMixin, ListView):
    model = Entry
    template_name = "entries/entry_list.html"
    context_object_name = "entries"
    paginate_by = 9

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        return context


class EntryDetailView(OwnerQuerysetMixin, DetailView):
    model = Entry
    template_name = "entries/entry_detail.html"


class EntryCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Entry
    form_class = EntryForm
    template_name = "entries/entry_form.html"
    success_message = "Запись создана"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class EntryUpdateView(OwnerQuerysetMixin, SuccessMessageMixin, UpdateView):
    model = Entry
    form_class = EntryForm
    template_name = "entries/entry_form.html"
    success_message = "Запись обновлена"


class EntryDeleteView(OwnerQuerysetMixin, DeleteView):
    model = Entry
    template_name = "entries/entry_confirm_delete.html"
    success_url = reverse_lazy("entries:list")
