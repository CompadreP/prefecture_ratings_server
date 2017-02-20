from rest_framework import serializers

from employees.models import RatingsUser, PrefectureEmployee, Organization


class RatingsUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingsUser
        fields = ('email', 'is_active', )


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ('name', )


class PrefectureEmployeeSerializer(serializers.ModelSerializer):
    user = RatingsUserSerializer()
    organization = OrganizationSerializer()

    class Meta:
        model = PrefectureEmployee
        fields = ('first_name', 'last_name', 'patronymic', 'user',
                  'organization', 'can_approve_rating')
