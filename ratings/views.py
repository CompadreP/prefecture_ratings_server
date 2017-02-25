from rest_framework import mixins
from rest_framework.decorators import list_route
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet

from common.response_wrappers import success_response
from ratings.models import MonthlyRating
from ratings.serializers import MonthlyRatingListSerializer, \
    MonthlyRatingDetailSerializer


class MonthlyRatingsViewSet(GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.RetrieveModelMixin):
    queryset = MonthlyRating.objects.all()
    serializer_class = MonthlyRatingDetailSerializer
    permission_classes = AllowAny

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = MonthlyRatingListSerializer(queryset, many=True)
        return success_response(serializer.data)

    @list_route(methods=['get'])
    def last_approved(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(
            queryset.filter(is_approved=True).first()
        )
        return success_response(serializer.data)

    @list_route(methods=['get'])
    def current(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        last_approved = queryset.filter(is_approved=True).first()
        if last_approved.month == 12:
            current_month = 1
            current_year = last_approved.year + 1
        else:
            current_month = last_approved.month + 1
            current_year = last_approved.year
        serializer = self.get_serializer(
            queryset.get(year=current_year, month=current_month)
        )
        return success_response(serializer.data)
