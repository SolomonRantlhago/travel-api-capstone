from rest_framework import serializers
from .models import Budget, BudgetExpense


class BudgetExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetExpense
        fields = ['id', 'budget', 'category', 'description', 'amount', 'date', 'created_at']
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'budget': {'write_only': True, 'required': False},
        }


class BudgetSerializer(serializers.ModelSerializer):
    itinerary_title = serializers.CharField(source='itinerary.title', read_only=True)
    total_spent = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    remaining = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    expenses = BudgetExpenseSerializer(many=True, read_only=True)

    class Meta:
        model = Budget
        fields = [
            'id', 'itinerary', 'itinerary_title', 'owner', 'total_limit',
            'currency', 'total_spent', 'remaining', 'expenses',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']