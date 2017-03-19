from django.db import transaction
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField

from apps.common.serializers import DynamicFieldsModelSerializer
from apps.employees.serializers import PrefectureEmployeeDetailSerializer
from apps.map.models import Region
from apps.ratings.models import MonthlyRating, BaseDocument, MonthlyRatingElement, \
    RatingElement, MonthlyRatingSubElement, MonthlyRatingSubElementValue


class MonthlyRatingListSerializer(DynamicFieldsModelSerializer):

    class Meta:
        model = MonthlyRating
        fields = ('id', 'year', 'month', 'is_negotiated', 'is_approved', )


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
                  'weight', 'sub_elements_display_type')


class MonthlyRatingElementSimpleSerializer(DynamicFieldsModelSerializer):
    rating_element = RatingElementSerializer()
    responsible = PrefectureEmployeeDetailSerializer(
        fields=('id', 'first_name', 'last_name', 'patronymic')
    )

    class Meta:
        model = MonthlyRatingElement
        fields = ('id', 'rating_element', 'responsible',
                  'additional_description', 'negotiator_comment',
                  'region_comment', 'values')


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
        fields = ('id', 'region', 'is_average', 'value', )


class MonthlyRatingSubElementSerializer(DynamicFieldsModelSerializer):
    responsible = PrefectureEmployeeDetailSerializer(
        fields=('id', 'first_name', 'last_name', 'patronymic')
    )
    values = MonthlyRatingSubElementValueSerializer(many=True)

    class Meta:
        model = MonthlyRatingSubElement
        fields = ('id', 'name', 'date', 'responsible', 'values', 'best_type',
                  'description', 'document', )


class MonthlyRatingElementDetailFullSerializer(DynamicFieldsModelSerializer):
    monthly_rating = MonthlyRatingListSerializer()
    rating_element = RatingElementSerializer()
    responsible = PrefectureEmployeeDetailSerializer(
        fields=('id', 'first_name', 'last_name', 'patronymic')
    )
    related_sub_elements = MonthlyRatingSubElementSerializer(many=True)

    class Meta:
        model = MonthlyRatingElement
        fields = ('id', 'monthly_rating', 'rating_element', 'responsible',
                  'values', 'related_sub_elements')


class MonthlyRatingElementDetailNoSubElementSerializer(DynamicFieldsModelSerializer):
    monthly_rating = MonthlyRatingListSerializer()
    rating_element = RatingElementSerializer()
    responsible = PrefectureEmployeeDetailSerializer(
        fields=('id', 'first_name', 'last_name', 'patronymic')
    )

    class Meta:
        model = MonthlyRatingElement
        fields = ('id', 'monthly_rating', 'rating_element', 'responsible',
                  'values')


class MonthlyRatingSubElementBaseChangeSerializer(DynamicFieldsModelSerializer):
    values = MonthlyRatingSubElementValueSerializer(many=True)

    class Meta:
        model = MonthlyRatingSubElement
        fields = ('id', 'name', 'date', 'responsible', 'values', 'best_type',
                  'description', )

    def validate_values(self, values):
        for value in values:
            value_id = value.get('id', None)
            if value_id:
                if MonthlyRatingSubElementValue.objects.get(pk=value_id).monthly_rating_sub_element != self.instance:
                    raise ValidationError('value belongs to another sub_element')
            if value['is_average'] and value['value']:
                raise ValidationError('both "is_average" and "value" set')
        return values


class MonthlyRatingSubElementCreateSerializer(MonthlyRatingSubElementBaseChangeSerializer):

    @transaction.atomic
    def create(self, validated_data):
        element = MonthlyRatingElement.objects.get(pk=self.context['element_id'])
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


class MonthlyRatingSubElementValueUpdateSerializer(MonthlyRatingSubElementValueSerializer):
    id = IntegerField(required=True)


class MonthlyRatingSubElementUpdateSerializer(MonthlyRatingSubElementBaseChangeSerializer):
    original_value_fields = set(MonthlyRatingSubElementValueSerializer.Meta.fields)
    original_value_fields.remove('region')
    values = MonthlyRatingSubElementValueUpdateSerializer(many=True, fields=tuple(original_value_fields))

    @transaction.atomic
    def update(self, instance, validated_data):
        values = validated_data.pop('values', None)
        # drop region if it is presented
        validated_data.pop('region', None)
        for value in values:
            value['monthly_rating_sub_element'] = instance
            MonthlyRatingSubElementValue.objects.update_or_create(
                pk=value.pop('id'),
                defaults=value
            )
        return instance
