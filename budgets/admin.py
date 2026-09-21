from django.contrib import admin
from .models import Budget, BudgetExpense


class BudgetExpenseInline(admin.TabularInline):
    model = BudgetExpense
    extra = 1


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['itinerary', 'owner', 'total_limit', 'currency']
    search_fields = ['itinerary__title', 'owner__username']
    inlines = [BudgetExpenseInline]


@admin.register(BudgetExpense)
class BudgetExpenseAdmin(admin.ModelAdmin):
    list_display = ['description', 'budget', 'category', 'amount', 'date']
    list_filter = ['category']