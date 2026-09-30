from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    BookingViewSet,
    AccommodationViewSet,
    ActivityViewSet,
    ActivityLogViewSet,
    bulk_update_bookings,
)


app_name = 'bookings'


router = DefaultRouter()
router.register(
    r'accommodations',
    AccommodationViewSet,
    basename='accommodation'
)
router.register(
    r'activities',
    ActivityViewSet,
    basename='activity'
)
router.register(
    r'logs',
    ActivityLogViewSet,
    basename='activity-log'
)
router.register(
    r'',
    BookingViewSet,
    basename='booking'
)

urlpatterns = [
    path(
        'bulk-update/',
        bulk_update_bookings,
        name='bulk-update',
    ),
] + router.urls
