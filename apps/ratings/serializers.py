from base64 import b64decode

from django.core.files.base import ContentFile
from django.db import transaction

from rest_framework.exceptions import ValidationError

from apps.common.exceptions import InvalidDocumentEncoding
from apps.common.serializers import DynamicFieldsModelSerializer
from apps.employees.serializers import PrefectureEmployeeDetailSerializer
from apps.map.models import Region
from apps.ratings.models import MonthlyRating, BaseDocument, \
    MonthlyRatingElement, RatingElement, MonthlyRatingSubElement, \
    MonthlyRatingSubElementValue


class MonthlyRatingListSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = MonthlyRating
        fields = ('id', 'year', 'month', 'is_negotiated', 'is_approved',)


class BaseDocumentSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = BaseDocument
        fields = ('id', 'kind', 'description', 'description_imp')


class RatingElementSerializer(DynamicFieldsModelSerializer):
    base_document = BaseDocumentSerializer(
        fields=('id', 'description', 'description_imp')
    )

    class Meta:
        model = RatingElement
        fields = ('id', 'number', 'base_document', 'name', 'base_description',
                  'weight', )


class MonthlyRatingElementSimpleSerializer(DynamicFieldsModelSerializer):
    rating_element = RatingElementSerializer()

    def __init__(self, *args, **kwargs):
        if not('context' in kwargs and kwargs['context'].get('method') == 'update'):
            self.fields['responsible'] = PrefectureEmployeeDetailSerializer(
                fields=('id', 'first_name', 'last_name', 'patronymic')
            )
        super(MonthlyRatingElementSimpleSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = MonthlyRatingElement
        fields = ('id', 'rating_element', 'responsible',
                  'additional_description', 'negotiator_comment',
                  'region_comment', 'best_type', 'values')


class MonthlyRatingDetailSerializer(DynamicFieldsModelSerializer):
    base_document = BaseDocumentSerializer(
        fields=('id', 'description', 'description_imp')
    )
    approved_by = PrefectureEmployeeDetailSerializer(
        fields=('id', 'first_name', 'last_name', 'patronymic')
    )
    elements = MonthlyRatingElementSimpleSerializer(many=True)

    class Meta:
        model = MonthlyRating
        fields = ('id', 'year', 'month', 'base_document', 'is_negotiated',
                  'is_approved', 'approved_by', 'elements')


class MonthlyRatingSubElementValueSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = MonthlyRatingSubElementValue
        fields = ('id', 'region', 'is_average', 'value',)


class MonthlyRatingElementDetailFullSerializer(DynamicFieldsModelSerializer):
    monthly_rating = MonthlyRatingListSerializer()
    rating_element = RatingElementSerializer()
    responsible = PrefectureEmployeeDetailSerializer(
        fields=('id', 'first_name', 'last_name', 'patronymic')
    )

    def __init__(self, *args, **kwargs):
        if 'context' in kwargs \
                and kwargs['context'].get('options') \
                and 'include_sub_elements' in kwargs['context'].get('options'):
            self.fields['related_sub_elements'] = MonthlyRatingSubElementRetrieveSerializer(many=True)
        super(MonthlyRatingElementDetailFullSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = MonthlyRatingElement
        fields = ('id', 'monthly_rating', 'rating_element', 'responsible',
                  'values', 'related_sub_elements', 'best_type')


class MonthlyRatingSubElementBaseSerializer(DynamicFieldsModelSerializer):
    values = MonthlyRatingSubElementValueSerializer(many=True)

    class Meta:
        model = MonthlyRatingSubElement
        fields = ('id', 'name', 'date', 'responsible', 'display_type',
                  'values', 'best_type', 'description', 'document', )

    def validate_name(self, name):
        if self.instance:
            if self.instance.monthly_rating_element.related_sub_elements\
                   .exclude(pk=self.instance.id)\
                   .filter(name=name)\
                   .exists():
                raise ValidationError(
                    'subelement with this name already exists')
        else:
            element_id = self.context.get('element_id')
            if element_id:
                if MonthlyRatingElement.objects\
                        .get(pk=element_id)\
                        .related_sub_elements\
                        .filter(name=name)\
                        .exists():
                    raise ValidationError(
                        'subelement with this name already exists')
        return name

    def validate_values(self, values):
        for value in values:
            if value['is_average'] and value['value']:
                raise ValidationError('both "is_average" and "value" set')
        return values


class MonthlyRatingSubElementRetrieveSerializer(MonthlyRatingSubElementBaseSerializer):
    responsible = PrefectureEmployeeDetailSerializer(
        fields=('id', 'first_name', 'last_name', 'patronymic')
    )


class MonthlyRatingSubElementChangeSerializer(MonthlyRatingSubElementBaseSerializer):

    def __init__(self, *args, **kwargs):
        if 'document' in kwargs['data']:
            document = kwargs['data'].get('document', None)
            if document:
                try:
                    document_base64_bin = document['data'].partition('base64,')[2]
                    document_raw_bin = b64decode(document_base64_bin)
                    converted_document = ContentFile(document_raw_bin)
                    converted_document.name = document['file_name']
                    kwargs['data']['document'] = converted_document
                except KeyError:
                    raise InvalidDocumentEncoding()
        super(MonthlyRatingSubElementChangeSerializer, self).__init__(*args, **kwargs)

    @transaction.atomic
    def create(self, validated_data):
        element = MonthlyRatingElement.objects.get(
            pk=self.context['element_id'])
        validated_data['monthly_rating_element'] = element
        values = validated_data.pop('values', None)
        instance = self.Meta.model.objects.create(**validated_data)
        all_regions = Region.objects.all()
        default_data = {
            'monthly_rating_sub_element': instance,
            'is_average': False,
            'value': None
        }
        for value in values:
            value['monthly_rating_sub_element'] = instance
            MonthlyRatingSubElementValue.objects.create(**value)
            all_regions = all_regions.exclude(pk=value['region'].id)
        for region in all_regions:
            default_data['region'] = region
            MonthlyRatingSubElementValue.objects.create(**default_data)
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        values = validated_data.pop('values', None)
        for value in values:
            value_instance = instance.values.get(region=value['region'])
            value_instance.is_average = value['is_average']
            value_instance.value = value['value']
            value_instance.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
