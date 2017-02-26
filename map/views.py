from rest_framework import mixins
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet

from map.models import Region
from map.serializers import RegionSimpleSerializer


class RegionsViewSet(GenericViewSet,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin):
    queryset = Region.objects.all()
    serializer_class = RegionSimpleSerializer
    permission_classes = (AllowAny, )

