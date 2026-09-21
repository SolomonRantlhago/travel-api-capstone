from rest_framework import permissions


class IsBookingOwnerOrAdmin(permissions.BasePermission):
    """
    Only the user who made the booking, or an admin/staff user,
    can view, edit, or delete it.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True
        return obj.booked_by == request.user