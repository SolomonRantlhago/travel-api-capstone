from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from destinations.models import Destination


class Itinerary(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('planned', 'Planned'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(max_length=1000, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='itineraries'
    )
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Itineraries'
        indexes = [
            models.Index(fields=['status'], name='itinerary_status_idx'),
        ]

    def __str__(self):
        return f"{self.title} ({self.owner.username})"

    def calculate_duration(self):
        return (self.end_date - self.start_date).days + 1

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError(
                "End date cannot be before start date."
            )


class ItineraryItem(models.Model):
    itinerary = models.ForeignKey(
        Itinerary,
        on_delete=models.CASCADE,
        related_name='items'
    )
    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name='itinerary_items'
    )
    day_number = models.PositiveIntegerField()
    notes = models.TextField(max_length=500, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['day_number', 'order']
        unique_together = ['itinerary', 'destination', 'day_number']

    def __str__(self):
        return f"Day {self.day_number}: {self.destination.name} ({self.itinerary.title})"