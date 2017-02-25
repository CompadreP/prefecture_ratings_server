from common.serializers import DynamicFieldsModelSerializer
from employees.serializers import PrefectureEmployeeSerializer
from ratings.models import MonthlyRating, BaseDocument, MonthlyRatingComponent, \
    RatingComponent


class MonthlyRatingListSerializer(DynamicFieldsModelSerializer):

    class Meta:
        model = MonthlyRating
        fields = ('id', 'year', 'month', 'is_approved', )


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


class MonthlyRatingComponentSerializer(DynamicFieldsModelSerializer):
    rating_component = RatingComponentSerializer()
    responsible = PrefectureEmployeeSerializer(
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
    approved_by = PrefectureEmployeeSerializer(
        fields=('id', 'first_name', 'last_name', 'patronymic')
    )
    components = MonthlyRatingComponentSerializer(many=True)

    class Meta:
        model = MonthlyRating
        fields = ('id', 'year', 'month', 'base_document', 'is_negotiated',
                  'is_approved', 'approved_by', 'components')
