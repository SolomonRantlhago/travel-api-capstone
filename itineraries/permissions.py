from rest_framework import permissions


class IsOwnerOrAdminOrReadOnlyIfPublic(permissions.BasePermission):
    """
    - Owner can always view/edit/delete their own itinerary.
    - Staff/superuser can always view/edit/delete any itinerary.
    - Anyone else can only VIEW (GET) if the itinerary is public.
    - Anyone else has no access if the itinerary is private.
    """

    def has_object_permission(self, request, view, obj):

        if request.user.is_staff or request.user.is_superuser:
            return True

        if obj.owner == request.user:
            return True

        if request.method in permissions.SAFE_METHODS and obj.is_public:
            return True

        return False


class IsItineraryItemOwnerOrAdmin(permissions.BasePermission):
    """
    Only the owner of the item's itinerary, or an admin/staff user,
    can access the itinerary item.
    """

    def has_object_permission(self, request, view, obj):

        if request.user.is_staff or request.user.is_superuser:
            return True

        return obj.itinerary.owner == request.user