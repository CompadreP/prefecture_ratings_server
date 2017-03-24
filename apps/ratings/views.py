from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework import mixins
from rest_framework import status
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.common.permissions import SubElementPermission, \
    MonthlyRatingElementPermission, MonthlyRatingPermission
from apps.common.response_wrappers import bad_request_response
from apps.ratings.models import MonthlyRating, MonthlyRatingElement, \
    MonthlyRatingSubElement
from apps.ratings.serializers import MonthlyRatingListSerializer, \
    MonthlyRatingDetailSerializer, MonthlyRatingElementDetailFullSerializer, \
    MonthlyRatingSubElementCreateSerializer, \
    MonthlyRatingElementSimpleSerializer, \
    MonthlyRatingSubElementRetrieveSerializer, \
    MonthlyRatingSubElementBaseSerializer, \
    MonthlyRatingSubElementUpdateSerializer


class MonthlyRatingsViewSet(GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.RetrieveModelMixin):
    queryset = MonthlyRating.objects.all()
    serializer_class = MonthlyRatingDetailSerializer
    permission_classes = (MonthlyRatingPermission,)

    @method_decorator(ensure_csrf_cookie)
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = MonthlyRatingListSerializer(queryset, many=True)
        return Response(serializer.data)

    @detail_route(methods=['patch'])
    @method_decorator(csrf_protect)
    def change_state(self, request, *args, **kwargs):
        rating = self.get_object()
        if request.data.get('is_negotiated') is True:
            rating.negotiate()
        elif request.data.get('is_approved') is True:
            if rating.is_negotiated is False:
                return Response(data={'detail': 'wrong rating state'},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                rating.approve()
        return Response(status=status.HTTP_200_OK)

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
            current = queryset.filter(year=current_year,
                                      month=current_month).first()
            if current:
                serializer = self.get_serializer(current)
            else:
                return Response(data={'detail': 'no_current_rating'},
                                status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = self.get_serializer(queryset.first())
        return Response(serializer.data)


class MonthlyRatingElementsViewSet(GenericViewSet,
                                   mixins.RetrieveModelMixin,
                                   mixins.UpdateModelMixin):
    queryset = MonthlyRatingElement.objects.all()
    serializer_class = MonthlyRatingElementSimpleSerializer
    permission_classes = (MonthlyRatingElementPermission,)

    @method_decorator(ensure_csrf_cookie)
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        include_related = request.query_params.get(
            'include_sub_elements') == 'true'

        context = {}
        if include_related:
            context['options'] = ['include_sub_elements']
        serializer = MonthlyRatingElementDetailFullSerializer(instance,
                                                              context=context)
        return Response(serializer.data)

    def get_serializer_context(self):
        context = {}
        if self.request.method == 'PATCH':
            context['method'] = 'update'
        return context


class MonthlyRatingSubElementsViewSet(GenericViewSet,
                                      mixins.RetrieveModelMixin,
                                      mixins.CreateModelMixin,
                                      mixins.UpdateModelMixin,
                                      mixins.DestroyModelMixin):
    queryset = MonthlyRatingSubElement.objects.all()
    permission_classes = (SubElementPermission,)

    @method_decorator(ensure_csrf_cookie)
    def retrieve(self, request, *args, **kwargs):
        return super(MonthlyRatingSubElementsViewSet, self).retrieve(request,
                                                                     *args,
                                                                     **kwargs)

    @method_decorator(csrf_protect)
    def create(self, request, *args, **kwargs):
        # document = request.data.pop('document', None)
        # # document = request.data.FILES.get('file')
        # if document:
        #     # TODO handle document
        #     pass
        try:
            request.query_params.get('element_id')
        except (KeyError, TypeError):
            return bad_request_response(error_code='wrong_element_id')
        if not MonthlyRatingElement.objects.filter(
                    pk=request.query_params.get('element_id')
                ).exists():
            return bad_request_response(error_code='wrong_element_id')
        return super(MonthlyRatingSubElementsViewSet, self).create(request,
                                                                   *args,
                                                                   **kwargs)

    @method_decorator(csrf_protect)
    def update(self, request, *args, **kwargs):
        # document = request.data.pop('document', None)
        # # document = request.data.FILES.get('file')
        # if document:
        #     # TODO handle document
        #     pass
        return super(MonthlyRatingSubElementsViewSet, self).update(request,
                                                                   *args,
                                                                   **kwargs)

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        if self.request.method == 'GET':
            serializer_class = MonthlyRatingSubElementRetrieveSerializer
        elif self.request.method == 'PATCH':
            serializer_class = MonthlyRatingSubElementUpdateSerializer
        elif self.request.method == 'POST':
            serializer_class = MonthlyRatingSubElementCreateSerializer
            kwargs['context']['element_id'] = int(
                self.request.query_params.get('element_id'))
        else:
            serializer_class = self.get_serializer_class()
        return serializer_class(*args, **kwargs)
