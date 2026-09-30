from rest_framework import permissions


def get_collaboration_role(user, itinerary):
    """
    Return the user's collaborator role on the itinerary
    ('viewer', 'editor' or 'admin'), or None if they are not a collaborator.
    """
    return itinerary.collaborations.filter(
        user=user
    ).values_list('role', flat=True).first()


class IsItineraryItemOwnerOrAdmin(permissions.BasePermission):
    """
    Role-based access to the items inside an itinerary.

    * Read (GET/HEAD/OPTIONS): owner, any collaborator, site admins,
      and anyone at all if the itinerary is public.
    * Write (POST/PUT/PATCH/DELETE): owner, site admins, and collaborators
      whose role is 'editor' or 'admin'. Viewers are read-only.

    The itinerary comes from the URL, so this is checked in
    has_permission() via the view's get_itinerary() helper.
    """

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        itinerary = view.get_itinerary()

        if user.is_site_admin or itinerary.owner_id == user.id:
            return True

        is_read = request.method in permissions.SAFE_METHODS
        if is_read and itinerary.is_public:
            return True

        role = get_collaboration_role(user, itinerary)
        if role is None:
            return False

        return is_read or role in ('editor', 'admin')

    def has_object_permission(self, request, view, obj):
        # Same rules for a single item, resolved through its itinerary.
        user = request.user
        if user.is_site_admin or obj.itinerary.owner_id == user.id:
            return True

        role = get_collaboration_role(user, obj.itinerary)
        if role is None:
            return False

        return (
            request.method in permissions.SAFE_METHODS
            or role in ('editor', 'admin')
        )


class IsOwnerOrCollaboratorOrAdmin(permissions.BasePermission):
    """
    Object-level permission for an itinerary:
    site admins and the owner can do anything, collaborators are limited
    by their role, and public itineraries are readable by everyone.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Site admins can do anything
        if user.is_authenticated and user.is_site_admin:
            return True

        # Itinerary owner can do anything
        if obj.owner == user:
            return True

        if obj.is_public and request.method in permissions.SAFE_METHODS:
            return True

        # Check whether the user is a collaborator
        role = get_collaboration_role(user, obj)

        if role is None:
            return False

        # Viewers can only perform safe/read operations
        if request.method in permissions.SAFE_METHODS:
            return True

        # Editors and admins can modify the itinerary
        return role in ['editor', 'admin']


class IsItineraryOwnerOrAdmin(permissions.BasePermission):
    """
    Only the owner of the itinerary (or a site admin) may manage its
    collaborators. Works on ItineraryCollaboration objects.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        return user.is_site_admin or obj.itinerary.owner_id == user.id
