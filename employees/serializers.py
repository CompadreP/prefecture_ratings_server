from common.serializers import DynamicFieldsModelSerializer
from employees.models import RatingsUser, PrefectureEmployee, Organization
from map.serializers import DistrictSerializer, RegionSerializer


class RatingsUserSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = RatingsUser
        fields = ('email', 'is_active', )


class OrganizationSerializer(DynamicFieldsModelSerializer):
    district = DistrictSerializer()
    region = RegionSerializer()

    class Meta:
        model = Organization
        fields = ('id', 'name', 'district', 'region')


class EmployeeSerializer(DynamicFieldsModelSerializer):
    user = RatingsUserSerializer()
    organization = OrganizationSerializer()


class PrefectureEmployeeSerializer(EmployeeSerializer):

    class Meta:
        model = PrefectureEmployee
        fields = ('id', 'first_name', 'last_name', 'patronymic', 'user',
                  'organization', 'can_approve_rating')


class RegionEmployeeSerializer(EmployeeSerializer):

    class Meta:
        model = PrefectureEmployee
        fields = ('id', 'first_name', 'last_name', 'patronymic', 'user',
                  'organization')
