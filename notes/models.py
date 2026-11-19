from django.db import models


class Note(models.Model):
    title = models.CharField(max_length=255)
    # The Angular add dialog sends an empty string when no description is entered.
    content = models.TextField(blank=True)
    marked = models.BooleanField(default=False)
    trash = models.BooleanField(default=False)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.title
