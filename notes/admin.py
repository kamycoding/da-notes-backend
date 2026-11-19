from django.contrib import admin

from .models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ["title", "marked", "trash"]
    list_filter = ["marked", "trash"]
    search_fields = ["title", "content"]
