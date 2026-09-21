from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from .models import Budget, BudgetExpense
from .serializers import BudgetSerializer, BudgetExpenseSerializer
from .permissions import IsBudgetOwnerOrAdmin


class BudgetListCreateView(generics.ListCreateAPIView):
    """
    GET /api/budgets/ - list the logged-in user's own budgets (all if admin)
    POST /api/budgets/ - create a new budget for one of your own itineraries
    """
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Budget.objects.all()
        return Budget.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class BudgetDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PUT/PATCH/DELETE /api/budgets/<id>/ - manage a specific budget
    """
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated, IsBudgetOwnerOrAdmin]


class BudgetExpenseListCreateView(generics.ListCreateAPIView):
    """
    GET /api/budgets/<budget_id>/expenses/ - list expenses for one budget
    POST /api/budgets/<budget_id>/expenses/ - add a new expense (owner or admin only,
    rejected if it would exceed the budget's total_limit)
    """
    serializer_class = BudgetExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_budget(self):
        try:
            return Budget.objects.get(pk=self.kwargs['budget_id'])
        except Budget.DoesNotExist:
            raise NotFound("Budget not found.")

    def get_queryset(self):
        return BudgetExpense.objects.filter(budget_id=self.kwargs['budget_id'])

    def perform_create(self, serializer):
        budget = self.get_budget()
        user = self.request.user
        if not (budget.owner == user or user.is_staff or user.is_superuser):
            raise PermissionDenied("You do not own this budget.")

        new_amount = serializer.validated_data['amount']
        if budget.total_spent + new_amount > budget.total_limit:
            raise ValidationError(
                f"This expense would exceed the budget limit. "
                f"Remaining: {budget.remaining} {budget.currency}, attempted: {new_amount} {budget.currency}."
            )

        serializer.save(budget=budget)