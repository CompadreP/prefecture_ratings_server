from rest_framework import serializers

from apps.common.serializers import DynamicFieldsModelSerializer
from apps.map.models import District, Region


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ('id', 'name', )


class RegionSerializer(DynamicFieldsModelSerializer):
    district = DistrictSerializer()

    class Meta:
        model = Region
        fields = ('id', 'name', 'district')


class RegionSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Region
        fields = ('id', 'name', 'district', )
