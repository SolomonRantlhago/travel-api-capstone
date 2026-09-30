from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model with additional profile fields.
    """
    class Role(models.TextChoices):
        TRAVELER = 'traveler', 'Traveler'
        ADMIN = 'admin', 'Admin'

    email = models.EmailField(unique=True)

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default='traveler'
    )
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(
        upload_to='profiles/',
        null=True,
        blank=True
    )
    travel_preferences = models.JSONField(default=dict, blank=True)

    favorite_destinations = models.ManyToManyField(
        'destinations.Destination',
        blank=True,
        related_name='favorited_by'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username

    @property
    def is_site_admin(self):
        """True for staff, superusers and users with the admin role."""
        return bool(
            self.is_staff
            or self.is_superuser
            or self.role == self.Role.ADMIN
        )
