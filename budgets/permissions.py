from rest_framework import permissions


class IsBudgetOwnerOrAdmin(permissions.BasePermission):
    """
    Only the budget's owner, or an admin/staff user,
    can view, edit, or delete it. Budgets are private financial data.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True
        return obj.owner == request.user