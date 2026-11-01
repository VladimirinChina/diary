from typing import Any

from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.forms import ModelForm
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import LoginForm, RegisterForm


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("entries:list")

    def form_valid(self, form: "ModelForm[Any]") -> HttpResponse:
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class UserLoginView(LoginView):
    authentication_form = LoginForm
    template_name = "registration/login.html"
