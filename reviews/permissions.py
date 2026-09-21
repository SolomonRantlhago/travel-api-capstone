from rest_framework import permissions


class IsReviewOwnerOrAdminOrReadOnly(permissions.BasePermission):
    """
    Anyone can read reviews. Only the review's author, or an admin/staff
    user, can update or delete it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_staff or request.user.is_superuser:
            return True
        return obj.reviewer == request.user