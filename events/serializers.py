from rest_framework import serializers

from events.models import Event


class EventSerializer(serializers.ModelSerializer):
    organizer = serializers.SlugRelatedField(slug_field="email", read_only=True)

    class Meta:
        model = Event
        fields = ("id", "title", "description", "date", "location", "organizer", "participants", )


class EventParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ("id", )
