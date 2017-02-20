from rest_framework import serializers

from employees.models import RatingsUser, PrefectureEmployee, Organization
from map.serializers import DistrictSerializer, RegionSerializer


class RatingsUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingsUser
        fields = ('email', 'is_active', )


class OrganizationSerializer(serializers.ModelSerializer):
    district = DistrictSerializer()
    region = RegionSerializer()

    class Meta:
        model = Organization
        fields = ('name', 'district', 'region')


class EmployeeSerializer(serializers.ModelSerializer):
    user = RatingsUserSerializer()
    organization = OrganizationSerializer()


class PrefectureEmployeeSerializer(EmployeeSerializer):

    class Meta:
        model = PrefectureEmployee
        fields = ('first_name', 'last_name',
                  'patronymic', 'user', 'organization', 'can_approve_rating')


class RegionEmployeeSerializer(EmployeeSerializer):

    class Meta:
        model = PrefectureEmployee
        fields = ('first_name', 'last_name',
                  'patronymic', 'user', 'organization')
