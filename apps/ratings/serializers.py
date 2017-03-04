from django.db import transaction
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField

from apps.common.serializers import DynamicFieldsModelSerializer
from apps.employees.serializers import PrefectureEmployeeDetailSerializer
from apps.map.models import Region
from apps.ratings.models import MonthlyRating, BaseDocument, MonthlyRatingComponent, \
    RatingComponent, MonthlyRatingSubComponent, MonthlyRatingSubComponentValue


class MonthlyRatingListSerializer(DynamicFieldsModelSerializer):

    class Meta:
        model = MonthlyRating
        fields = ('id', 'year', 'month', 'is_negotiated', 'is_approved', )


class BaseDocumentSerializer(DynamicFieldsModelSerializer):

    class Meta:
        model = BaseDocument
        fields = ('id', 'kind', 'description', 'description_imp')


class RatingComponentSerializer(DynamicFieldsModelSerializer):
    base_document = BaseDocumentSerializer(
        fields=('id', 'description', 'description_imp')
    )

    class Meta:
        model = RatingComponent
        fields = ('id', 'number', 'base_document', 'name', 'base_description',
                  'weight', 'sub_components_display_type')


class MonthlyRatingComponentSimpleSerializer(DynamicFieldsModelSerializer):
    rating_component = RatingComponentSerializer()
    responsible = PrefectureEmployeeDetailSerializer(
        fields=('id', 'first_name', 'last_name', 'patronymic')
    )

    class Meta:
        model = MonthlyRatingComponent
        fields = ('id', 'rating_component', 'responsible',
                  'additional_description', 'negotiator_comment',
                  'region_comment', 'values')


class MonthlyRatingDetailSerializer(DynamicFieldsModelSerializer):
    base_document = BaseDocumentSerializer(
        fields=('id', 'description', 'description_imp')
    )
    approved_by = PrefectureEmployeeDetailSerializer(
        fields=('id', 'first_name', 'last_name', 'patronymic')
    )
    components = MonthlyRatingComponentSimpleSerializer(many=True)

    class Meta:
        model = MonthlyRating
        fields = ('id', 'year', 'month', 'base_document', 'is_negotiated',
                  'is_approved', 'approved_by', 'components')


class MonthlyRatingSubComponentValueSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = MonthlyRatingSubComponentValue
        fields = ('id', 'region', 'is_average', 'value', )


class MonthlyRatingSubComponentSerializer(DynamicFieldsModelSerializer):
    responsible = PrefectureEmployeeDetailSerializer(
        fields=('id', 'first_name', 'last_name', 'patronymic')
    )
    values = MonthlyRatingSubComponentValueSerializer(many=True)

    class Meta:
        model = MonthlyRatingSubComponent
        fields = ('id', 'name', 'date', 'responsible', 'values', 'best_type',
                  'description', 'document', )


class MonthlyRatingComponentDetailFullSerializer(DynamicFieldsModelSerializer):
    monthly_rating = MonthlyRatingListSerializer()
    rating_component = RatingComponentSerializer()
    responsible = PrefectureEmployeeDetailSerializer(
        fields=('id', 'first_name', 'last_name', 'patronymic')
    )
    related_sub_components = MonthlyRatingSubComponentSerializer(many=True)

    class Meta:
        model = MonthlyRatingComponent
        fields = ('id', 'monthly_rating', 'rating_component', 'responsible',
                  'values', 'related_sub_components')


class MonthlyRatingComponentDetailNoSubComponentsSerializer(DynamicFieldsModelSerializer):
    monthly_rating = MonthlyRatingListSerializer()
    rating_component = RatingComponentSerializer()
    responsible = PrefectureEmployeeDetailSerializer(
        fields=('id', 'first_name', 'last_name', 'patronymic')
    )

    class Meta:
        model = MonthlyRatingComponent
        fields = ('id', 'monthly_rating', 'rating_component', 'responsible',
                  'values')


class MonthlyRatingSubComponentBaseChangeSerializer(DynamicFieldsModelSerializer):
    values = MonthlyRatingSubComponentValueSerializer(many=True)

    class Meta:
        model = MonthlyRatingSubComponent
        fields = ('id', 'name', 'date', 'responsible', 'values', 'best_type',
                  'description', )

    def validate_values(self, values):
        for value in values:
            value_id = value.get('id', None)
            if value_id:
                if MonthlyRatingSubComponentValue.objects.get(pk=value_id).monthly_rating_sub_component != self.instance:
                    raise ValidationError('value belongs to another sub_component')
            if value['is_average'] and value['value']:
                raise ValidationError('both "is_average" and "value" set')
        return values


class MonthlyRatingSubComponentCreateSerializer(MonthlyRatingSubComponentBaseChangeSerializer):

    @transaction.atomic
    def create(self, validated_data):
        component = MonthlyRatingComponent.objects.get(pk=self.context['component_id'])
        validated_data['monthly_rating_component'] = component
        values = validated_data.pop('values', None)
        instance = self.Meta.model.objects.create(**validated_data)
        all_regions = Region.objects.all()
        default_data = {
            'monthly_rating_sub_component': instance,
            'is_average': False,
            'value': None
        }
        for value in values:
            value['monthly_rating_sub_component'] = instance
            MonthlyRatingSubComponentValue.objects.create(**value)
            all_regions = all_regions.exclude(pk=value['region'].id)
        for region in all_regions:
            default_data['region'] = region
            MonthlyRatingSubComponentValue.objects.create(**default_data)
        return instance


class MonthlyRatingSubComponentValueUpdateSerializer(MonthlyRatingSubComponentValueSerializer):
    id = IntegerField(required=True)


class MonthlyRatingSubComponentUpdateSerializer(MonthlyRatingSubComponentBaseChangeSerializer):
    original_value_fields = set(MonthlyRatingSubComponentValueSerializer.Meta.fields)
    original_value_fields.remove('region')
    values = MonthlyRatingSubComponentValueUpdateSerializer(many=True, fields=tuple(original_value_fields))

    @transaction.atomic
    def update(self, instance, validated_data):
        values = validated_data.pop('values', None)
        # drop region if it is presented
        validated_data.pop('region', None)
        for value in values:
            value['monthly_rating_sub_component'] = instance
            MonthlyRatingSubComponentValue.objects.update_or_create(
                pk=value.pop('id'),
                defaults=value
            )
        return instance
