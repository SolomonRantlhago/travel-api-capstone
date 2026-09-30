from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    BudgetListCreateView,
    BudgetDetailView,
    BudgetExpenseListCreateView,
    BudgetReadOnlyViewSet,
    budget_summary,
)

app_name = 'budgets'

router = DefaultRouter()

router.register(
    r'read-only',
    BudgetReadOnlyViewSet,
    basename='budget-read-only'
)


urlpatterns = [
    path(
        '',
        BudgetListCreateView.as_view(),
        name='budget-list-create'
    ),
    path(
        '<int:pk>/',
        BudgetDetailView.as_view(),
        name='budget-detail'
    ),
    path(
        '<int:budget_id>/expenses/',
        BudgetExpenseListCreateView.as_view(),
        name='budget-expense-list-create'
    ),
    path(
        '<int:pk>/summary/',
        budget_summary,
        name='budget-summary'
    ),
] + router.urls
