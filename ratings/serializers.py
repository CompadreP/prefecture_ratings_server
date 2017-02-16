from rest_framework import serializers

from ratings.models import MonthlyRating


class MonthlyRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyRating
        fields = ('id', 'is_negotiated', 'is_approved', 'year', 'month')
