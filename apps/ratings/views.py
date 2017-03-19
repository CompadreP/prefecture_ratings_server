from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework import mixins
from rest_framework import status
from rest_framework.decorators import list_route, detail_route
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.common.permissions import NegotiatorOnlyPermission, \
    ResponsibleOnlyPermission, SubElementPermission, AdminOnlyPermission
from apps.common.response_wrappers import bad_request_response
from apps.ratings.models import MonthlyRating, MonthlyRatingElement, \
    MonthlyRatingSubElement
from apps.ratings.serializers import MonthlyRatingListSerializer, \
    MonthlyRatingDetailSerializer, MonthlyRatingElementDetailFullSerializer, \
    MonthlyRatingSubElementCreateSerializer, \
    MonthlyRatingSubElementSerializer, \
    MonthlyRatingElementDetailNoSubElementSerializer, \
    MonthlyRatingSubElementUpdateSerializer


class MonthlyRatingsViewSet(GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.RetrieveModelMixin):
    queryset = MonthlyRating.objects.all()
    serializer_class = MonthlyRatingDetailSerializer
    permission_classes = (AllowAny, )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = MonthlyRatingListSerializer(queryset, many=True)
        return Response(serializer.data)

    @list_route(methods=['get'])
    @method_decorator(ensure_csrf_cookie)
    def last_approved(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        last_approved = queryset.filter(is_approved=True).first()
        if last_approved:
            serializer = self.get_serializer(last_approved)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @list_route(methods=['get'])
    @method_decorator(ensure_csrf_cookie)
    def current(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        last_approved = queryset.filter(is_approved=True).first()
        if last_approved:
            if last_approved.month == 12:
                current_month = 1
                current_year = last_approved.year + 1
            else:
                current_month = last_approved.month + 1
                current_year = last_approved.year
            serializer = self.get_serializer(
                queryset.get(year=current_year, month=current_month)
            )
        else:
            serializer = self.get_serializer(queryset.first())
        return Response(serializer.data)


class MonthlyRatingElementsViewSet(GenericViewSet,
                                   mixins.RetrieveModelMixin,):
    queryset = MonthlyRatingElement.objects.all()
    permission_classes = (AllowAny, )

    @method_decorator(ensure_csrf_cookie)
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        include_related = request.query_params.get('include_sub_elements') == 'true'
        if include_related:
            serializer = MonthlyRatingElementDetailFullSerializer(instance)
        else:
            serializer = MonthlyRatingElementDetailNoSubElementSerializer(instance)
        return Response(serializer.data)

    @detail_route(methods=['patch'], permission_classes=[AdminOnlyPermission])
    @method_decorator(csrf_protect)
    def additional_description(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.additional_description = str(request.data['additional_description'])
            instance.save()
        except KeyError:
            return bad_request_response('incorrect_fields_set')
        return Response()

    @detail_route(methods=['patch'], permission_classes=[NegotiatorOnlyPermission])
    @method_decorator(csrf_protect)
    def negotiator_comment(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.negotiator_comment = str(request.data['negotiator_comment'])
            instance.save()
        except KeyError:
            return bad_request_response('incorrect_fields_set')
        return Response()

    @detail_route(methods=['patch'], permission_classes=[ResponsibleOnlyPermission])
    @method_decorator(csrf_protect)
    def region_comment(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.region_comment = str(request.data['region_comment'])
            instance.save()
        except KeyError:
            return bad_request_response('incorrect_fields_set')
        return Response()


class MonthlyRatingSubElementsViewSet(GenericViewSet,
                                      mixins.RetrieveModelMixin,
                                      mixins.CreateModelMixin,
                                      mixins.UpdateModelMixin,
                                      mixins.DestroyModelMixin):
    queryset = MonthlyRatingSubElement.objects.all()
    permission_classes = (SubElementPermission,)

    @method_decorator(ensure_csrf_cookie)
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = MonthlyRatingSubElementSerializer(instance)
        return Response(serializer.data)

    @method_decorator(csrf_protect)
    def create(self, request, *args, **kwargs):
        document = request.data.pop('document', None)
        # document = request.data.FILES.get('file')
        if document:
            # TODO handle document
            pass
        try:
            element_id = int(request.query_params.get('element_id'))
        except (KeyError, TypeError):
            return bad_request_response(error_code='wrong_element_id')
        serializer = MonthlyRatingSubElementCreateSerializer(
            data=request.data,
            context={'element_id': element_id}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    @method_decorator(csrf_protect)
    def update(self, request, *args, **kwargs):
        document = request.data.pop('document', None)
        if document:
            # TODO handle document
            pass
        instance = self.get_object()
        if request.user.prefectureemployee == instance.monthly_rating_element.responsible:
            serializer = MonthlyRatingSubElementUpdateSerializer(instance, data=request.data)
        elif request.user.prefectureemployee == instance.responsible:
            fields = set(MonthlyRatingSubElementUpdateSerializer.Meta.fields)
            fields.remove('responsible')
            serializer = MonthlyRatingSubElementUpdateSerializer(instance, data=request.data, fields=tuple(fields))
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        return Response(serializer.data)
