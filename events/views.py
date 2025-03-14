from django.shortcuts import render
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters import rest_framework as filters
from django_filters.filters import DateFromToRangeFilter


from events.models import Event
from events.permissions import IsOwnerUserOrReadOnlyOrAdmin
from events.serializers import EventSerializer, EventParticipantSerializer
from events.tasks import send_notification


class EventFilter(filters.FilterSet):
    title = filters.CharFilter(
        field_name="title",
        lookup_expr="icontains"
    )
    description = filters.CharFilter(
        field_name="description",
        lookup_expr="icontains"
    )
    location = filters.CharFilter(
        field_name="location",
        lookup_expr="icontains"
    )
    date = DateFromToRangeFilter(field_name="date")

    class Meta:
        model = Event
        fields = [
            "title",
            "description",
            "location",
            "date",
        ]


@extend_schema_view(
    list=extend_schema(
        summary="List of all Events",
        parameters=[
            OpenApiParameter(
                "date_after",
                type=OpenApiTypes.DATE,
                description="Filter by date after this date "
                "(ex. ?date_after=value). ",
            ),
            OpenApiParameter(
                "date_before",
                type=OpenApiTypes.DATE,
                description="Filter by date before this date "
                            "(ex. ?date_before=value). ",
            ),
            OpenApiParameter(
                "title",
                type=OpenApiTypes.STR,
                required=False,
                description="Filter by title contains "
                            "(ex. ?title=value - for title, that contains value)",
            ),
            OpenApiParameter(
                "location",
                type=OpenApiTypes.STR,
                required=False,
                description="Filter by location contains "
                            "(ex. ?location=value - for location, that contains value)",
            ),
            OpenApiParameter(
                "description",
                type=OpenApiTypes.STR,
                required=False,
                description="Filter by description contains "
                            "(ex. ?description=value - for title, that contains value)",
            ),
        ]
    ),
    create=extend_schema(summary="Add new event", ),
    retrieve=extend_schema(summary="Get event object by id", ),
    update=extend_schema(summary="Update event object by id", ),
    partial_update=extend_schema(summary="Partial update event object by id", ),
    destroy=extend_schema(summary="Delete event object by id", ),
    register=extend_schema(summary="Add user to event participants", ),
    unregister=extend_schema(summary="Remove user from event participants", ),
)
class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    permission_classes = (IsOwnerUserOrReadOnlyOrAdmin, )
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = EventFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related('participants')

    def get_serializer_class(self):
        if self.action in ("register", "unregister"):
            return EventParticipantSerializer
        return EventSerializer

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

    @action(detail=True, methods=["POST"], permission_classes=[IsAuthenticated])
    def register(self, request, pk=None):
        """Add current user to participants of event"""
        event = self.get_object()
        event.participants.add(self.request.user)
        subject = "You have successfully registered."
        message = (f"Add {self.request.user.email} to event: {event.title} | {event.location} "
                   f"at {event.date.strftime('%d/%m/%Y')}")
        print(f"To: {self.request.user.email} Subject: {subject}: |Message: {message}")
        send_notification.delay(subject, message, None, self.request.user.email)
        return Response({"detail": message}, status=status.HTTP_201_CREATED, )

    @action(detail=True, methods=["POST"], permission_classes=[IsAuthenticated])
    def unregister(self, request, pk=None):
        """Remove current user from participants of event"""
        event = self.get_object()
        event.participants.remove(self.request.user)
        subject = "You have unregistered."
        message = (f"Remove {self.request.user.email} from event: {event.title} | {event.location} "
                   f"at {event.date.strftime('%d/%m/%Y')}")
        print(f"To: {self.request.user.email} Subject: {subject}: |Message: {message}")
        send_notification.delay(subject, message, None, self.request.user.email)
        return Response({"detail": message}, status=status.HTTP_204_NO_CONTENT, )
