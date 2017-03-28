import datetime
from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.db import transaction
from django.urls import reverse
from django.utils.safestring import mark_safe

from apps.ratings.models import RatingElement, BaseDocument, SignerText, \
    MonthlyRating, MonthlyRatingElement


class SignerTextForm(forms.ModelForm):
    model = SignerText

    def clean_is_active(self):
        if self.cleaned_data['is_active'] is True:
            if self.instance.id:
                exists = SignerText.objects.filter(is_active=True).exclude(pk=self.instance.id).exists()
            else:
                exists = SignerText.objects.filter(is_active=True).exists()
            if exists:
                raise ValidationError("Может быть только один активный текст "
                                      "подписанта, сначала деактивируйте "
                                      "существующий активный.")


class SignerTextAdmin(admin.ModelAdmin):
    form = SignerTextForm
    list_display = ('id', 'text', 'is_active',)


class BaseDocumentAdmin(admin.ModelAdmin):
    pass


class RatingElementForm(forms.ModelForm):
    model = RatingElement

    def clean(self):
        valid_from_year = self.cleaned_data['valid_from_year']
        valid_from_month = self.cleaned_data['valid_from_month']
        valid_to_year = self.cleaned_data['valid_to_year']
        valid_to_month = self.cleaned_data['valid_to_month']
        # both fields filled
        super(RatingElementForm, self).clean()
        if ((valid_to_year and not valid_to_month)
                or
                (not valid_to_year and valid_to_month)):
            raise ValidationError('Если заполнено хоть одно из значений '
                                  '"Действует по месяц" или "Действует по год", '
                                  'то второе тоже должно быть заполнено')
        # to is bigger than from
        if valid_to_year and valid_to_month:
            date_from = datetime.date(year=valid_from_year, month=valid_from_month, day=1)
            date_to = datetime.date(year=valid_to_year, month=valid_to_month, day=1)
            if date_to < date_from:
                raise ValidationError('Окончание периода действия не может быть '
                                      'раньше начала')
            if date_to == date_from:
                raise ValidationError('Даты начала и окончания периодов действия '
                                      'не должны совпадать')

        # periods intersection
        intersect_message = 'Нельзя создавать базовый компонент рейтинга' \
                            ' с таким же наименованием, как и у ' \
                            'существующего и пересекающимися сроками действия.'

        if not self.instance.id:
            if valid_to_year and valid_to_month:
                if (RatingElement.objects
                        .filter(name=self.cleaned_data['name'].strip())
                        .filter(valid_from_year__lte=valid_to_year)
                        .filter(valid_from_month__lte=valid_to_month)
                        .filter(valid_to_year__gte=valid_from_year)
                        .filter(valid_to_month__gte=valid_from_month)
                        .exists()):
                    raise ValidationError(intersect_message)
                if (RatingElement.objects
                        .filter(name=self.cleaned_data['name'].strip())
                        .filter(valid_from_year__lte=valid_to_year)
                        .filter(valid_from_month__lte=valid_to_month)
                        .filter(valid_to_year=None)
                        .filter(valid_to_month=None)
                        .exists()):
                    raise ValidationError(intersect_message)
            else:
                if (RatingElement.objects
                        .filter(name=self.cleaned_data['name'].strip())
                        .filter(valid_to_year=None)
                        .filter(valid_to_month=None)
                        .exists()):
                    raise ValidationError(intersect_message)
                elif (RatingElement.objects
                        .filter(name=self.cleaned_data['name'].strip())
                        .filter(valid_from_year__lte=valid_from_year)
                        .filter(valid_from_month__lte=valid_from_year)
                        .filter(valid_to_year__gte=valid_from_year)
                        .filter(valid_to_month__gte=valid_from_month)
                        .exists()):
                    raise ValidationError(intersect_message)
        else:
            if valid_to_year and valid_to_month:
                if (RatingElement.objects
                        .exclude(pk=self.instance.id)
                        .filter(name=self.cleaned_data['name'].strip())
                        .filter(valid_from_year__lte=valid_to_year)
                        .filter(valid_from_month__lte=valid_to_month)
                        .filter(valid_to_year__gte=valid_from_year)
                        .filter(valid_to_month__gte=valid_from_month)
                        .exists()):
                    raise ValidationError(intersect_message)
                if (RatingElement.objects
                        .exclude(pk=self.instance.id)
                        .filter(name=self.cleaned_data['name'].strip())
                        .filter(valid_from_year__lte=valid_to_year)
                        .filter(valid_from_month__lte=valid_to_month)
                        .filter(valid_to_year=None)
                        .filter(valid_to_month=None)
                        .exists()):
                    raise ValidationError(intersect_message)
            else:
                if (RatingElement.objects
                        .exclude(pk=self.instance.id)
                        .filter(name=self.cleaned_data['name'].strip())
                        .filter(valid_to_year=None)
                        .filter(valid_to_month=None)
                        .exists()):
                    raise ValidationError(intersect_message)
                elif (RatingElement.objects
                        .exclude(pk=self.instance.id)
                        .filter(name=self.cleaned_data['name'].strip())
                        .filter(valid_from_year__lte=valid_from_year)
                        .filter(valid_from_month__lte=valid_from_year)
                        .filter(valid_to_year__gte=valid_from_year)
                        .filter(valid_to_month__gte=valid_from_month)
                        .exists()):
                    raise ValidationError(intersect_message)


class RatingElementAdmin(admin.ModelAdmin):
    form = RatingElementForm
    list_display = ('id', 'is_active', 'name', 'responsible',
                    'base_document', 'valid_from_month', 'valid_from_year',
                    'valid_to_month', 'valid_to_year', )

    def is_active(self, obj):
        return obj.is_active

    is_active.short_description = 'Активен'
    is_active.boolean = True
    is_active.admin_order_field = 'is_active'


class MonthlyRatingElementInlineAdmin(admin.StackedInline):
    model = MonthlyRatingElement
    readonly_fields = ('negotiator_comment', 'rating_element',
                       'region_comment', 'rating_element_url')
    fields = ('rating_element_url', 'number', 'responsible',
              'additional_description', 'negotiator_comment', 'region_comment')
    ordering = ('id', )

    def rating_element_url(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse('admin:ratings_ratingelement_change', args=[obj.id]),
            str(obj.rating_element))
        )

    rating_element_url.short_description = RatingElement._meta.verbose_name

    def has_add_permission(self, request):
        return False


class MonthlyRatingAdmin(admin.ModelAdmin):
    inlines = [MonthlyRatingElementInlineAdmin]
    readonly_fields = ('is_negotiated', 'is_approved', 'approved_by',
                       # 'year', 'month',
                       )
    fieldsets = (
        ('Информация', {
            'fields': ('year', 'month', 'is_negotiated', 'is_approved',
                       'approved_by', ),
        }),
        ('Редактирование', {
            'fields': ('base_document', 'signer_text')
        }),
    )
    actions = ['generate_elements']

    # def has_add_permission(self, request):
    #     return False

    def has_delete_permission(self, request, obj=None):
        return False

    @transaction.atomic
    def generate_elements(self, request, queryset):
        if queryset.count() > 1:
            messages.error(request, "Данное действие доступно только для единичных объектов")
        else:
            rating = queryset.get()
            rating_start_date = datetime.date(year=rating.year, month=rating.month, day=1)
            rating_elements = RatingElement.objects.all()
            created = 0
            skipped = 0
            for rating_element in rating_elements:
                if rating_element.is_active_on_date(rating_start_date):
                    if MonthlyRatingElement.objects.filter(
                            monthly_rating=rating,
                            rating_element=rating_element).exists():
                        skipped += 1
                        messages.warning(
                            request,
                            "Для данного рейтинга компонент с базовым компонентом {} уже создан".format(str(rating_element))
                        )
                    else:
                        MonthlyRatingElement.objects.create(
                            number=created + 1,
                            monthly_rating=rating,
                            rating_element=rating_element,
                            responsible=rating_element.responsible
                        )
                        created += 1
            message = "Создано - {} компонентов, пропущено - {} компонентов".format(created, skipped)
            if created:
                messages.info(request, message)
            else:
                messages.error(request, message)

    generate_elements.short_description = "Сгенерировать компоненты для месячного рейтинга"

admin.site.register(SignerText, SignerTextAdmin)
admin.site.register(RatingElement, RatingElementAdmin)
admin.site.register(BaseDocument, BaseDocumentAdmin)
admin.site.register(MonthlyRating, MonthlyRatingAdmin)
