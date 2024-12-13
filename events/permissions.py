from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerUserOrReadOnlyOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        return request.method in SAFE_METHODS or obj.organizer == request.user or request.user.is_staff
