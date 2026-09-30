from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from itineraries.models import Itinerary
from destinations.models import Destination


class Accommodation(models.Model):
    """
    Hotels, hostels, vacation rentals and similar places to stay.
    """

    class TypeChoices(models.TextChoices):
        HOTEL = 'hotel', 'Hotel'
        HOSTEL = 'hostel', 'Hostel'
        RENTAL = 'rental', 'Vacation Rental'
        RESORT = 'resort', 'Resort'
        BNB = 'bnb', 'B&B'

    name = models.CharField(max_length=200)
    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name='accommodations'
    )
    accommodation_type = models.CharField(
        max_length=10,
        choices=TypeChoices.choices,
        default=TypeChoices.HOTEL
    )
    description = models.TextField(blank=True)
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    max_guests = models.PositiveIntegerField(default=2)
    amenities = models.JSONField(default=list, blank=True)
    address = models.CharField(max_length=300, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    image = models.ImageField(
        upload_to='accommodations/',
        null=True,
        blank=True
    )
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(
                fields=['destination', 'accommodation_type'],
                name='accommodation_dest_type_idx'
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_accommodation_type_display()})"


class Activity(models.Model):
    """
    Tours, attractions and experiences users can reserve.
    """

    class CategoryChoices(models.TextChoices):
        TOUR = 'tour', 'Tour'
        ATTRACTION = 'attraction', 'Attraction'
        DINING = 'dining', 'Dining'
        SHOPPING = 'shopping', 'Shopping'
        ENTERTAINMENT = 'entertainment', 'Entertainment'
        OUTDOOR = 'outdoor', 'Outdoor'

    name = models.CharField(max_length=200)
    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    category = models.CharField(
        max_length=20,
        choices=CategoryChoices.choices,
        default=CategoryChoices.TOUR
    )
    description = models.TextField(blank=True)
    duration_hours = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=1.0,
        validators=[MinValueValidator(0)]
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    max_participants = models.PositiveIntegerField(null=True, blank=True)
    requirements = models.TextField(blank=True)
    image = models.ImageField(
        upload_to='activities/',
        null=True,
        blank=True
    )
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Activities'
        indexes = [
            models.Index(
                fields=['destination', 'category'],
                name='activity_dest_cat_idx'
            ),
        ]

    def __str__(self):
        return f"{self.name} - {self.destination.name}"


class Booking(models.Model):
    """
    User booking for an itinerary, optionally tied to a specific
    accommodation or activity.
    """

    class StatusChoices(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'
        COMPLETED = 'completed', 'Completed'

    class PaymentStatusChoices(models.TextChoices):
        UNPAID = 'unpaid', 'Unpaid'
        PAID = 'paid', 'Paid'
        REFUNDED = 'refunded', 'Refunded'

    itinerary = models.ForeignKey(
        Itinerary,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    booked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    accommodation = models.ForeignKey(
        Accommodation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings'
    )
    activity = models.ForeignKey(
        Activity,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings'
    )
    reference_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatusChoices.choices,
        default=PaymentStatusChoices.UNPAID
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    currency = models.CharField(max_length=3, default='USD')
    booking_date = models.DateField()
    check_in = models.DateField(null=True, blank=True)
    check_out = models.DateField(null=True, blank=True)
    guests_count = models.PositiveIntegerField(default=1)
    notes = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status'], name='booking_status_idx'),
            models.Index(
                fields=['booked_by', 'status'],
                name='booking_user_status_idx'
            ),
        ]

    def __str__(self):
        if self.accommodation:
            return (
                f"Booking {self.reference_number}: "
                f"{self.accommodation.name}"
            )
        if self.activity:
            return (
                f"Booking {self.reference_number}: "
                f"{self.activity.name}"
            )
        return f"Booking {self.reference_number} - {self.itinerary.title}"

    def clean(self):
        if self.accommodation and self.activity:
            raise ValidationError(
                'Booking cannot have both accommodation and activity.'
            )
        if self.check_in and self.check_out and self.check_out < self.check_in:
            raise ValidationError('Check-out must be on or after check-in.')

    def is_active(self):
        return self.status in [
            self.StatusChoices.PENDING,
            self.StatusChoices.CONFIRMED,
        ]


class ActivityLog(models.Model):
    """
    Audit trail of important actions across the travel API.
    """

    class ActionChoices(models.TextChoices):
        CREATE = 'create', 'Create'
        UPDATE = 'update', 'Update'
        DELETE = 'delete', 'Delete'
        BOOK = 'book', 'Book'
        CANCEL = 'cancel', 'Cancel'
        CONFIRM = 'confirm', 'Confirm'
        SHARE = 'share', 'Share'
        LOGIN = 'login', 'Login'
        EXPORT = 'export', 'Export'
        OTHER = 'other', 'Other'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activity_logs'
    )
    action = models.CharField(
        max_length=20,
        choices=ActionChoices.choices,
        default=ActionChoices.OTHER
    )
    entity_type = models.CharField(max_length=50)
    entity_id = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(max_length=500, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(
                fields=['user', 'created_at'],
                name='log_user_time_idx'
            ),
            models.Index(
                fields=['entity_type', 'entity_id'],
                name='log_entity_idx'
            ),
        ]

    def __str__(self):
        who = self.user.username if self.user else 'system'
        return (
            f"{who} {self.action} "
            f"{self.entity_type}#{self.entity_id or '-'}"
        )
