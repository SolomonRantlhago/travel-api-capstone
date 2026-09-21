from django.db import models
from django.conf import settings


class Destination(models.Model):
    """
    A travel destination that users can add to itineraries.
    """
    CATEGORY_CHOICES = [
        ('beach', 'Beach'),
        ('mountain', 'Mountain'),
        ('city', 'City'),
        ('countryside', 'Countryside'),
        ('cultural', 'Cultural/Historical'),
        ('adventure', 'Adventure'),
    ]

    PRICE_RANGE_CHOICES = [
        ('budget', 'Budget'),
        ('moderate', 'Moderate'),
        ('luxury', 'Luxury'),
    ]

    name = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True)
    description = models.TextField(max_length=1000)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price_range = models.CharField(max_length=20, choices=PRICE_RANGE_CHOICES)
    image = models.ImageField(
        upload_to='destinations/',
        null=True,
        blank=True
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    best_season = models.CharField(max_length=100, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='destinations_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category'], name='destination_category_idx'),
        ]

    def __str__(self):
        return f"{self.name}, {self.country}"

    def get_full_location(self):
        return f"{self.city}, {self.country}" if self.city else self.country


class Amenity(models.Model):
    """
    An amenity or facility available at a destination.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class DestinationAmenity(models.Model):
    """
    Connects a destination to an amenity while storing
    additional information about that relationship.
    """
    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name='destination_amenities'
    )
    amenity = models.ForeignKey(
        Amenity,
        on_delete=models.CASCADE,
        related_name='destination_amenities'
    )
    is_free = models.BooleanField(default=True)
    notes = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['destination', 'amenity']
        constraints = [
            models.UniqueConstraint(
                fields=['destination', 'amenity'],
                name='unique_destination_amenity'
            )
        ]

    def __str__(self):
        return f"{self.destination.name} - {self.amenity.name}"