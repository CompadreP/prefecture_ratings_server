from rest_framework import permissions
from rest_framework.permissions import BasePermission

from apps.employees.models import PrefectureEmployee
from apps.ratings.models import MonthlyRatingElement


class AdminOnlyPermission(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_admin:
            return True
        else:
            return False


class NegotiatorOnlyPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        if PrefectureEmployee.objects.filter(user=request.user.id).exists():
            if request.user.prefectureemployee.can_approve_rating:
                return True
            else:
                return False
        else:
            return False


class ResponsibleOnlyPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        if PrefectureEmployee.objects.filter(user=request.user.id).exists():
            if request.user.prefectureemployee == obj.responsible:
                return True
            else:
                return False
        else:
            return False


class SubElementPermission(BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            if request.user.is_anonymous:
                return False
            if PrefectureEmployee.objects.filter(user=request.user.id).exists():
                if request.method == 'POST':
                    component = MonthlyRatingElement.objects.get(pk=request.query_params['component_id'])
                    if component.responsible == request.user.prefectureemployee:
                        return True
                    else:
                        return False
                else:
                    return True
            else:
                return False

    def has_object_permission(self, request, view, obj):
        if request.method in ['PUT', 'DELETE']:
            employee = request.user.prefectureemployee
            return obj.responsible == employee \
                   or obj.monthly_rating_component.responsible == employee
        else:
            return True
