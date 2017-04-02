from django.contrib.auth.models import Group
from rest_framework import permissions
from rest_framework.permissions import BasePermission

from apps.ratings.models import MonthlyRatingElement


class MonthlyRatingPermission(BasePermission):
    def has_object_permission(self, request, view, obj: MonthlyRatingElement):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            if Group.objects.get(name='prefecture') in request.user.groups.all():
                return request.user.prefectureemployee.can_approve_rating
            else:
                return False


class MonthlyRatingElementPermission(BasePermission):
    def has_object_permission(self, request, view, obj: MonthlyRatingElement):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            if request.user.is_anonymous:
                return False
            if request.method == 'PATCH':
                request_data_len = len(request.data)
                if 'responsible' in request.data:
                    return request.user.is_admin and request_data_len == 1
                if 'negotiator_comment' in request.data:
                    if Group.objects.get(name='prefecture') in request.user.groups.all():
                        return request.user.prefectureemployee.can_approve_rating and request_data_len == 1
                    else:
                        return False
                if 'additional_description' in request.data:
                    if Group.objects.get(name='prefecture') in request.user.groups.all():
                        return request.user.prefectureemployee == obj.responsible and request_data_len == 1
                if 'region_comment' in request.data:
                    if Group.objects.get(name='prefecture') in request.user.groups.all():
                        return request.user.prefectureemployee == obj.responsible and request_data_len == 1
                    else:
                        return False
            else:
                return False
        return False


class SubElementPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            if request.user.is_anonymous:
                return False
            if Group.objects.get(name='prefecture') in request.user.groups.all():
                if request.method == 'POST':
                    element = MonthlyRatingElement.objects.get(
                        pk=request.query_params['element_id'])
                    return element.responsible == request.user.prefectureemployee
                else:
                    return True
            else:
                return False

    def has_object_permission(self, request, view, obj):
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            employee = request.user.prefectureemployee
            return obj.responsible == employee \
                   or obj.monthly_rating_element.responsible == employee

