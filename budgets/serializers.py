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

    def update(self, instance, validated_data):
        validated_data.pop('budget', None)

        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()

        return instance


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

    def get_budget_status(self, obj) -> str:
        if obj.total_spent == 0:
            return "Not started"

        if obj.total_spent < obj.total_limit:
            return "Within budget"

        if obj.total_spent == obj.total_limit:
            return "Budget reached"

        return "Over budget"

    def validate_itinerary(self, value):
        """
        A budget can only be attached to an itinerary the user owns
        (site admins may attach to any), and cannot be moved to a
        different itinerary once created.
        """
        request = self.context.get('request')

        if self.instance is not None and value != self.instance.itinerary:
            raise serializers.ValidationError(
                "A budget cannot be moved to a different itinerary."
            )

        if request and not request.user.is_site_admin:
            if value.owner_id != request.user.id:
                raise serializers.ValidationError(
                    "You can only create budgets for your own itineraries."
                )

        return value

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
