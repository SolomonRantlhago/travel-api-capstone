from django.db import models
from django.conf import settings
from itineraries.models import Itinerary


class Budget(models.Model):
    """
    A spending plan for a trip — a total limit split across categories.
    """
    CATEGORY_CHOICES = [
        ('accommodation', 'Accommodation'),
        ('transport', 'Transport'),
        ('food', 'Food & Drink'),
        ('activities', 'Activities'),
        ('shopping', 'Shopping'),
        ('other', 'Other'),
    ]

    itinerary = models.OneToOneField(
        Itinerary,
        on_delete=models.CASCADE,
        related_name='budget'
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='budgets'
    )
    total_limit = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Budget for {self.itinerary.title} ({self.total_limit} {self.currency})"

    @property
    def total_spent(self):
        return sum(expense.amount for expense in self.expenses.all())

    @property
    def remaining(self):
        return self.total_limit - self.total_spent


class BudgetExpense(models.Model):
    """
    A single tracked expense against a trip's budget.
    """
    budget = models.ForeignKey(
        Budget,
        on_delete=models.CASCADE,
        related_name='expenses'
    )
    category = models.CharField(max_length=20, choices=Budget.CATEGORY_CHOICES)
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.description}: {self.amount} ({self.budget.itinerary.title})"