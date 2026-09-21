from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from destinations.models import Destination


class Review(models.Model):
    """
    A user's rating and comment on a destination.
    """
    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(max_length=1000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['destination', 'reviewer']

    def __str__(self):
        return f"{self.reviewer.username} rated {self.destination.name}: {self.rating}/5"