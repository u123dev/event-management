from django.urls import include, path
from rest_framework import routers

from events.views import EventViewSet

app_name = "events"

router = routers.DefaultRouter()
router.register("", EventViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
