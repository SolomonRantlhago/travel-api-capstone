from rest_framework import generics, permissions, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.exceptions import (
    NotFound,
    PermissionDenied,
    ValidationError,
)
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count, F, Prefetch


from .models import Budget, BudgetExpense
from .serializers import BudgetSerializer, BudgetExpenseSerializer
from .permissions import (
    IsBudgetOwnerOrAdmin,
    IsBudgetExpenseOwnerOrAdmin,
)


class BudgetListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/budgets/ - list your budgets
    POST /api/v1/budgets/ - create a budget for one of YOUR itineraries

    Example request (POST):
        {"itinerary": 12, "total_limit": "1500.00", "currency": "USD"}

    Example response (201): the budget with total_spent 0 and
    remaining equal to total_limit. Using someone else's itinerary
    returns a 400.
    """
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Budget.objects.none()

        user = self.request.user

        base = Budget.objects.select_related(
            'itinerary',
            'owner'
        ).prefetch_related(
            Prefetch(
                'expenses',
                queryset=BudgetExpense.objects.order_by('-date')
            )
        ).order_by('-created_at')

        # Admin users can view budgets belonging to all users.
        if user.is_staff or user.is_superuser:
            return base.all()

        return base.filter(owner=user)

    def perform_create(self, serializer):
        # Defense in depth: serializer.validate_itinerary already rejects
        # foreign itineraries, but re-check here before save.
        itinerary = serializer.validated_data.get('itinerary')
        user = self.request.user
        if (
            itinerary is not None
            and not user.is_site_admin
            and itinerary.owner_id != user.id
        ):
            raise PermissionDenied(
                "You can only create budgets for your own itineraries."
            )
        serializer.save(owner=user)


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


class BudgetReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only access to budgets.
    Only GET requests are allowed.
    """
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Budget.objects.none()
        user = self.request.user

        base = Budget.objects.select_related(
            'itinerary',
            'owner'
        ).prefetch_related(
            'expenses'
        ).order_by('-created_at')

        if user.is_staff or user.is_superuser:
            return base.all()

        return base.filter(owner=user)


class BudgetExpenseListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/budgets/<budget_id>/expenses/ - list expenses, newest first
    POST /api/v1/budgets/<budget_id>/expenses/ - record a new expense

    Example request (POST):
        {"category": "food", "description": "Dinner", "amount": "42.50",
         "date": "2026-11-06"}

    An expense that would push the budget over its limit is rejected (400).
    """
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
        if getattr(self, 'swagger_fake_view', False):
            return BudgetExpense.objects.none()

        budget = self.get_budget()
        user = self.request.user
        # Include the budget limit with each expense for
        # budget-related calculations.
        expenses = BudgetExpense.objects.annotate(
            budget_limit=F('budget__total_limit')
        )

        if user.is_staff or user.is_superuser:
            return expenses.filter(
                budget=budget
            ).order_by(
                F('date').desc()
            )

        if budget.owner != user:
            raise PermissionDenied(
                "You do not own this budget."
            )

        return expenses.filter(
            budget=budget
        ).order_by(
            F('date').desc()
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

        # Prevent a new expense from pushing the budget
        # beyond its allowed limit.
        if budget.total_spent + new_amount > budget.total_limit:
            raise ValidationError(
                f"This expense would exceed the budget limit. "
                f"Remaining: {budget.remaining} {budget.currency}, "
                f"attempted: {new_amount} {budget.currency}."
            )
        # Associate the expense with the budget from the URL.
        serializer.save(budget=budget)


@extend_schema(
    responses=inline_serializer(
        name='BudgetSummaryResponse',
        fields={
            'budget_id': serializers.IntegerField(),
            'total_limit': serializers.DecimalField(
                max_digits=10,
                decimal_places=2
            ),
            'total_spent': serializers.DecimalField(
                max_digits=10,
                decimal_places=2
            ),
            'remaining': serializers.DecimalField(
                max_digits=10,
                decimal_places=2
            ),
            'currency': serializers.CharField(),
            'expense_count': serializers.IntegerField(),
            'status': serializers.CharField(),
        },
    )
)
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

    total_spent = budget.expenses.aggregate(
        total=Sum('amount')
    )['total'] or 0

    # Calculate how much of the budget is still available to spend.
    remaining = budget.total_limit - total_spent

    # Check the database total to determine whether
    # the budget has been exceeded.
    over_budget = Budget.objects.annotate(
        spent_total=Sum('expenses__amount')
    ).filter(
        pk=budget.pk,
        spent_total__gt=F('total_limit')
    ).exists()

    if total_spent == 0:
        status = "Not started"
    elif total_spent < budget.total_limit:
        status = "Within budget"
    elif total_spent == budget.total_limit:
        status = "Budget reached"
    elif over_budget:
        status = "Over budget"

    return Response(
        {
            "budget_id": budget.id,
            "total_limit": budget.total_limit,
            "total_spent": total_spent,
            "remaining": remaining,
            "currency": budget.currency,
            "expense_count": budget.expenses.aggregate(
                count=Count('id')
            )['count'],
            "status": status,
        },
        status=200
    )
