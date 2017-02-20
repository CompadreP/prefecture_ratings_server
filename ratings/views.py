from rest_framework import viewsets
from rest_framework.response import Response

from ratings.models import MonthlyRating
from ratings.serializers import MonthlyRatingSerializer


class RatingsViewSet(viewsets.ModelViewSet):
    queryset = MonthlyRating.objects.all()
    serializer_class = MonthlyRatingSerializer

    def list(self, request, *args, **kwargs):
        a = 1 / 0
        return Response(data={'success': True, 'a': a})
