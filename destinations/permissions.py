from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Anyone can read (GET/HEAD/OPTIONS).
    Only staff or superuser accounts can create, update, or delete.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and
                    (request.user.is_staff or request.user.is_superuser))