from django import forms

from .models import Entry


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ("title", "mood", "content")
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "mood": forms.Select(attrs={"class": "form-select"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 10}),
        }
