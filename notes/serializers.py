from rest_framework import serializers

from .models import Note


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ["id", "title", "content", "marked", "trash"]
        read_only_fields = ["id"]
        extra_kwargs = {"content": {"required": True}}
