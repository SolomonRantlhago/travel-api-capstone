from rest_framework import generics, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404

from .models import Budget, BudgetExpense
from .serializers import BudgetSerializer, BudgetExpenseSerializer
from .permissions import (
    IsBudgetOwnerOrAdmin,
    IsBudgetExpenseOwnerOrAdmin,
)


class BudgetListCreateView(generics.ListCreateAPIView):
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        base = Budget.objects.select_related(
            'itinerary',
            'owner'
        ).prefetch_related('expenses')

        if user.is_staff or user.is_superuser:
            return base.all()

        return base.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class BudgetDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Budget.objects.select_related(
        'itinerary',
        'owner'
    ).prefetch_related('expenses')
    serializer_class = BudgetSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsBudgetOwnerOrAdmin
    ]


class BudgetExpenseListCreateView(generics.ListCreateAPIView):
    serializer_class = BudgetExpenseSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsBudgetExpenseOwnerOrAdmin
    ]

    def get_budget(self):
        try:
            return Budget.objects.get(
                pk=self.kwargs['budget_id']
            )
        except Budget.DoesNotExist:
            raise NotFound("Budget not found.")

    def get_queryset(self):
        return BudgetExpense.objects.filter(
            budget_id=self.kwargs['budget_id']
        )

    def perform_create(self, serializer):
        budget = self.get_budget()
        user = self.request.user

        if not (
            budget.owner == user
            or user.is_staff
            or user.is_superuser
        ):
            raise PermissionDenied(
                "You do not own this budget."
            )

        new_amount = serializer.validated_data['amount']

        if budget.total_spent + new_amount > budget.total_limit:
            raise ValidationError(
                f"This expense would exceed the budget limit. "
                f"Remaining: {budget.remaining} {budget.currency}, "
                f"attempted: {new_amount} {budget.currency}."
            )

        serializer.save(budget=budget)


@api_view(['GET'])
def budget_summary(request, pk):
    """
    GET /api/v1/budgets/<id>/summary/
    Return a summary of the selected budget.
    """
    budget = get_object_or_404(
        Budget.objects.prefetch_related('expenses'),
        pk=pk
    )

    if not (
        budget.owner == request.user
        or request.user.is_staff
        or request.user.is_superuser
    ):
        return Response(
            {"detail": "You do not have permission to view this budget."},
            status=403
        )

    total_spent = budget.total_spent
    remaining = budget.total_limit - total_spent

    if total_spent == 0:
        status = "Not started"
    elif total_spent < budget.total_limit:
        status = "Within budget"
    elif total_spent == budget.total_limit:
        status = "Budget reached"
    else:
        status = "Over budget"

    return Response(
        {
            "budget_id": budget.id,
            "total_limit": budget.total_limit,
            "total_spent": total_spent,
            "remaining": remaining,
            "currency": budget.currency,
            "expense_count": budget.expenses.count(),
            "status": status,
        },
        status=200
    )