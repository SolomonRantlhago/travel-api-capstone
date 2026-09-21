from django.urls import path
from .views import BudgetListCreateView, BudgetDetailView, BudgetExpenseListCreateView

urlpatterns = [
    path('', BudgetListCreateView.as_view(), name='budget-list-create'),
    path('<int:pk>/', BudgetDetailView.as_view(), name='budget-detail'),
    path('<int:budget_id>/expenses/', BudgetExpenseListCreateView.as_view(), name='budget-expense-list-create'),
]