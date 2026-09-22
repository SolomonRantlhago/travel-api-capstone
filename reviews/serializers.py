from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    reviewer_username = serializers.CharField(
        source='reviewer.username',
        read_only=True
    )

    destination_name = serializers.CharField(
        source='destination.name',
        read_only=True
    )

    rating_label = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            'id',
            'destination',
            'destination_name',
            'reviewer',
            'reviewer_username',
            'rating',
            'rating_label',
            'comment',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'reviewer',
            'created_at',
            'updated_at'
        ]
        validators = []

    def get_rating_label(self, obj):
        return obj.rating_label()

    def validate(self, data):
        """
        Manually enforce one-review-per-user-per-destination,
        since the automatic unique_together validator requires
        'reviewer' in the request body, but we set it from the
        logged-in user instead.
        """
        request = self.context.get('request')
        destination = data.get('destination')

        if request and destination and self.instance is None:
            if Review.objects.filter(
                destination=destination,
                reviewer=request.user
            ).exists():
                raise serializers.ValidationError(
                    "You have already reviewed this destination."
                )

        return data