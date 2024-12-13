from django.contrib.auth import get_user_model
from django.db import models


class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    date = models.DateField(db_index=True)
    location = models.CharField(max_length=255)
    organizer = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="user_events")
    participants = models.ManyToManyField(get_user_model(), related_name="events", blank=True)

    class Meta:
        ordering = ["-date", ]

    def __str__(self):
        return f"{self.title} | {self.location} by {self.organizer} at {self.date}"
