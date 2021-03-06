from apps.common.serializers import DynamicFieldsModelSerializer
from apps.employees.models import RatingsUser, PrefectureEmployee, Organization, \
    RegionEmployee
from apps.map.serializers import DistrictSerializer, RegionSerializer


class RatingsUserSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = RatingsUser
        fields = ('email', 'is_active', )


class OrganizationSerializer(DynamicFieldsModelSerializer):
    district = DistrictSerializer()
    region = RegionSerializer(fields=('id', 'name', ))

    class Meta:
        model = Organization
        fields = ('id', 'name', 'district', 'region')


class EmployeeSerializer(DynamicFieldsModelSerializer):
    user = RatingsUserSerializer()
    organization = OrganizationSerializer()


class PrefectureEmployeeSimpleSerializer(EmployeeSerializer):

    class Meta:
        model = PrefectureEmployee
        fields = ('id', 'first_name', 'last_name', 'patronymic')


class PrefectureEmployeeDetailSerializer(EmployeeSerializer):

    class Meta:
        model = PrefectureEmployee
        fields = ('id', 'first_name', 'last_name', 'patronymic', 'user',
                  'organization', 'can_approve_rating')


class RegionEmployeeSerializer(EmployeeSerializer):

    class Meta:
        model = RegionEmployee
        fields = ('id', 'first_name', 'last_name', 'patronymic', 'user',
                  'organization')
