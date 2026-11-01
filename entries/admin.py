from django.contrib import admin

from .models import Entry


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "mood", "created_at", "updated_at")
    list_filter = ("author", "mood", "created_at")
    search_fields = ("title", "content")
