from rest_framework import serializers

from map.models import District, Region


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ('id', 'name', )


class RegionSerializer(serializers.ModelSerializer):
    district = DistrictSerializer()

    class Meta:
        model = Region
        fields = ('id', 'district', 'name', )


class RegionSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Region
        fields = ('id', 'name', 'district', )
