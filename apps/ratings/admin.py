import datetime
from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.db import transaction
from django.urls import reverse
from django.db.models import Q
from django.utils.safestring import mark_safe

from apps.ratings.models import RatingComponent, BaseDocument, SignerText, \
    MonthlyRating, MonthlyRatingComponent


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


class RatingComponentForm(forms.ModelForm):
    model = RatingComponent

    def clean(self):
        valid_from_year = self.cleaned_data['valid_from_year']
        valid_from_month = self.cleaned_data['valid_from_month']
        valid_to_year = self.cleaned_data['valid_to_year']
        valid_to_month = self.cleaned_data['valid_to_month']
        # both fields filled
        super(RatingComponentForm, self).clean()
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
                            ' с таким же номером или наименованием, как и у ' \
                            'существующего и пересекающимися сроками действия.'

        if not self.instance.id:
            if valid_to_year and valid_to_month:
                if (RatingComponent.objects
                        .filter(Q(number=self.cleaned_data['number']) | Q(name=self.cleaned_data['name'].strip()))
                        .filter(valid_from_year__lte=valid_to_year)
                        .filter(valid_from_month__lte=valid_to_month)
                        .filter(valid_to_year__gte=valid_from_year)
                        .filter(valid_to_month__gte=valid_from_month)
                        .exists()):
                    raise ValidationError(intersect_message)
                if (RatingComponent.objects
                        .filter(Q(number=self.cleaned_data['number']) | Q(name=self.cleaned_data['name'].strip()))
                        .filter(valid_from_year__lte=valid_to_year)
                        .filter(valid_from_month__lte=valid_to_month)
                        .filter(valid_to_year=None)
                        .filter(valid_to_month=None)
                        .exists()):
                    raise ValidationError(intersect_message)
            else:
                if (RatingComponent.objects
                        .filter(Q(number=self.cleaned_data['number']) | Q(name=self.cleaned_data['name'].strip()))
                        .filter(valid_to_year=None)
                        .filter(valid_to_month=None)
                        .exists()):
                    raise ValidationError(intersect_message)
                elif (RatingComponent.objects
                        .filter(Q(number=self.cleaned_data['number']) | Q(name=self.cleaned_data['name'].strip()))
                        .filter(valid_from_year__lte=valid_from_year)
                        .filter(valid_from_month__lte=valid_from_year)
                        .filter(valid_to_year__gte=valid_from_year)
                        .filter(valid_to_month__gte=valid_from_month)
                        .exists()):
                    raise ValidationError(intersect_message)
        else:
            if valid_to_year and valid_to_month:
                if (RatingComponent.objects
                        .exclude(pk=self.instance.id)
                        .filter(Q(number=self.cleaned_data['number']) | Q(name=self.cleaned_data['name'].strip()))
                        .filter(valid_from_year__lte=valid_to_year)
                        .filter(valid_from_month__lte=valid_to_month)
                        .filter(valid_to_year__gte=valid_from_year)
                        .filter(valid_to_month__gte=valid_from_month)
                        .exists()):
                    raise ValidationError(intersect_message)
                if (RatingComponent.objects
                        .exclude(pk=self.instance.id)
                        .filter(Q(number=self.cleaned_data['number']) | Q(name=self.cleaned_data['name'].strip()))
                        .filter(valid_from_year__lte=valid_to_year)
                        .filter(valid_from_month__lte=valid_to_month)
                        .filter(valid_to_year=None)
                        .filter(valid_to_month=None)
                        .exists()):
                    raise ValidationError(intersect_message)
            else:
                if (RatingComponent.objects
                        .exclude(pk=self.instance.id)
                        .filter(Q(number=self.cleaned_data['number']) | Q(name=self.cleaned_data['name'].strip()))
                        .filter(valid_to_year=None)
                        .filter(valid_to_month=None)
                        .exists()):
                    raise ValidationError(intersect_message)
                elif (RatingComponent.objects
                        .exclude(pk=self.instance.id)
                        .filter(Q(number=self.cleaned_data['number']) | Q(name=self.cleaned_data['name'].strip()))
                        .filter(valid_from_year__lte=valid_from_year)
                        .filter(valid_from_month__lte=valid_from_year)
                        .filter(valid_to_year__gte=valid_from_year)
                        .filter(valid_to_month__gte=valid_from_month)
                        .exists()):
                    raise ValidationError(intersect_message)


class RatingComponentAdmin(admin.ModelAdmin):
    form = RatingComponentForm
    list_display = ('id', 'is_active', 'number', 'name', 'responsible',
                    'base_document', 'valid_from_month', 'valid_from_year',
                    'valid_to_month', 'valid_to_year', )

    def is_active(self, obj):
        return obj.is_active

    is_active.short_description = 'Активен'
    is_active.boolean = True
    is_active.admin_order_field = 'is_active'


class MonthlyRatingComponentInlineAdmin(admin.StackedInline):
    model = MonthlyRatingComponent
    readonly_fields = ('negotiator_comment', 'rating_component',
                       'region_comment', 'rating_component_url')
    fields = ('rating_component_url', 'responsible', 'additional_description',
              'negotiator_comment', 'region_comment')
    ordering = ('rating_component__number', )

    def rating_component_url(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse('admin:ratings_ratingcomponent_change', args=[obj.id]),
            str(obj.rating_component))
        )

    rating_component_url.short_description = RatingComponent._meta.verbose_name

    def has_add_permission(self, request):
        return False


class MonthlyRatingAdmin(admin.ModelAdmin):
    inlines = [MonthlyRatingComponentInlineAdmin]
    readonly_fields = ('is_negotiated', 'is_approved', 'approved_by',
                       'year', 'month', )
    fieldsets = (
        ('Информация', {
            'fields': ('year', 'month', 'is_negotiated', 'is_approved',
                       'approved_by', ),
        }),
        ('Редактирование', {
            'fields': ('base_document', 'signer_text')
        }),
    )
    actions = ['generate_components']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @transaction.atomic
    def generate_components(self, request, queryset):
        if queryset.count() > 1:
            messages.error(request, "Данное действие доступно только для единичных объектов")
        else:
            rating = queryset.get()
            rating_start_date = datetime.date(year=rating.year, month=rating.month, day=1)
            rating_components = RatingComponent.objects.all()
            created = 0
            skipped = 0
            for rating_component in rating_components:
                if rating_component.is_active_on_date(rating_start_date):
                    if MonthlyRatingComponent.objects.filter(
                            monthly_rating=rating,
                            rating_component=rating_component).exists():
                        skipped += 1
                        messages.warning(
                            request,
                            "Для данного рейтинга компонент с базовым компонентом {} уже создан".format(str(rating_component))
                        )
                    else:
                        MonthlyRatingComponent.objects.create(
                            monthly_rating=rating,
                            rating_component=rating_component,
                            responsible=rating_component.responsible
                        )
                        created += 1
            message = "Создано - {} компонентов, пропущено - {} компонентов".format(created, skipped)
            if created:
                messages.info(request, message)
            else:
                messages.error(request, message)

    generate_components.short_description = "Сгенерировать компоненты для месячного рейтинга"

admin.site.register(SignerText, SignerTextAdmin)
admin.site.register(RatingComponent, RatingComponentAdmin)
admin.site.register(BaseDocument, BaseDocumentAdmin)
admin.site.register(MonthlyRating, MonthlyRatingAdmin)
