from rest_framework import serializers
from .models import Budget, BudgetExpense


class BudgetExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetExpense
        fields = [
            'id',
            'budget',
            'category',
            'description',
            'amount',
            'date',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'budget': {'write_only': True, 'required': False},
        }

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Expense amount must be greater than zero."
            )

        return value


class BudgetSerializer(serializers.ModelSerializer):
    itinerary_title = serializers.CharField(
        source='itinerary.title',
        read_only=True
    )

    total_spent = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    remaining = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    budget_status = serializers.SerializerMethodField()

    expenses = BudgetExpenseSerializer(
        many=True,
        read_only=True
    )

    def get_budget_status(self, obj):
        if obj.total_spent == 0:
            return "Not started"

        if obj.total_spent < obj.total_limit:
            return "Within budget"

        if obj.total_spent == obj.total_limit:
            return "Budget reached"

        return "Over budget"

    def validate(self, data):
        total_limit = data.get('total_limit')

        if total_limit is not None and total_limit <= 0:
            raise serializers.ValidationError(
                "Budget total limit must be greater than zero."
            )

        return data

    class Meta:
        model = Budget
        fields = [
            'id',
            'itinerary',
            'itinerary_title',
            'owner',
            'total_limit',
            'currency',
            'total_spent',
            'remaining',
            'budget_status',
            'expenses',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'owner',
            'created_at',
            'updated_at'
        ]