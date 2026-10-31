from django import forms

from .models import Entry


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ("title", "content")
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 10}),
        }
