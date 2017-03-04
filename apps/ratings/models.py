import datetime
from typing import List, Dict

from decimal import Decimal
from django.db import models

from apps.employees.models import PrefectureEmployee
from apps.map.models import Region

YEAR_CHOICES = [(r, r) for r in
                range(2016, datetime.date.today().year + 2)]

MONTH_CHOICES = [
    (1, 'Январь'),
    (2, 'Февраль'),
    (3, 'Март'),
    (4, 'Апрель'),
    (5, 'Май'),
    (6, 'Июнь'),
    (7, 'Июль'),
    (8, 'Август'),
    (9, 'Сентябрь'),
    (10, 'Октябрь'),
    (11, 'Ноябрь'),
    (12, 'Декабрь'),
]


class SignerText(models.Model):
    text = models.TextField(verbose_name="Текст", unique=True)
    is_active = models.BooleanField(
        verbose_name='Активный',
        default=False
    )

    class Meta:
        verbose_name = 'Текст подписанта'
        verbose_name_plural = 'Тексты подписантов'

    def __str__(self):
        return self._meta.verbose_name + ' , id - {}'.format(self.id)


class BaseDocument(models.Model):
    BASE_DOCUMENT_CHOICES = [
        (1, 'Основной'),
        (2, 'Показатель'),
    ]
    kind = models.IntegerField(verbose_name='Тип документа', choices=BASE_DOCUMENT_CHOICES)
    description = models.TextField(verbose_name='Наименование', unique=True)
    description_imp = models.TextField(verbose_name='Наименование (повелительное)', unique=True)

    class Meta:
        verbose_name = 'Документ-основание'
        verbose_name_plural = 'Документы-основания'

    def __str__(self):
        return self.description


class MonthlyRating(models.Model):
    base_document = models.ForeignKey(
        BaseDocument,
        verbose_name=BaseDocument._meta.verbose_name,
        on_delete=models.PROTECT
    )
    is_negotiated = models.BooleanField(default=False,
                                        verbose_name='Согласован')
    is_approved = models.BooleanField(default=False,
                                      verbose_name='Утвержден')
    approved_by = models.ForeignKey(PrefectureEmployee,
                                    verbose_name='Утвердивший сотрудник',
                                    null=True,
                                    on_delete=models.SET_NULL)
    year = models.SmallIntegerField(verbose_name='Год',
                                    choices=YEAR_CHOICES,)
    month = models.SmallIntegerField(verbose_name='Месяц',
                                     choices=MONTH_CHOICES,)
    signer_text = models.ForeignKey(
        SignerText,
        verbose_name=SignerText._meta.verbose_name,
        on_delete=models.PROTECT
    )

    class Meta:
        unique_together = ('year', 'month')
        ordering = ('-year', '-month')
        verbose_name = 'Месячный рейтинг'
        verbose_name_plural = 'Месячные рейтинги'

    def __str__(self):
        return 'Год - {}, месяц - {}'.format(self.year, self.month)

    def approve(self):
        # TODO on approve save to mongo fully serialized and generate excel
        pass

    def send_negotiation_emails(self):
        # mass mail
        pass

    def send_approved_emails(self):
        # mass mail
        pass


class RatingComponent(models.Model):
    DISPLAY_TYPE_CHOICES = [
        (1, 'десятичное число'),
        (2, 'процент'),
    ]
    WEIGHT_CHOICES = [(r, r) for r in
                      range(1, 11)]
    number = models.PositiveIntegerField(verbose_name='№ п/п')
    base_document = models.ForeignKey(BaseDocument,
                                      verbose_name='Документ-основание')
    name = models.TextField(verbose_name='Наименование')
    base_description = models.TextField(verbose_name='Базовое описание',
                                        null=True,
                                        blank=True)
    weight = models.SmallIntegerField(
        verbose_name='Вес',
        choices=WEIGHT_CHOICES
    )
    sub_components_display_type = models.SmallIntegerField(
        verbose_name='Тип отображения подкомпонентов',
        choices=DISPLAY_TYPE_CHOICES
    )
    responsible = models.ForeignKey(PrefectureEmployee,
                                    on_delete=models.SET_NULL,
                                    null=True,
                                    blank=True,
                                    verbose_name='Ответственный (базовый)')
    valid_from_month = models.SmallIntegerField(verbose_name='Действует с месяца',
                                                choices=MONTH_CHOICES,
                                                db_index=True)
    valid_from_year = models.SmallIntegerField(verbose_name='Действует с года',
                                               choices=YEAR_CHOICES,
                                               db_index=True)
    valid_to_month = models.SmallIntegerField(verbose_name='Действует по месяц(включительно)',
                                              choices=MONTH_CHOICES,
                                              null=True,
                                              blank=True,
                                              db_index=True)
    valid_to_year = models.SmallIntegerField(verbose_name='Действует по год(включительно)',
                                             choices=YEAR_CHOICES,
                                             null=True,
                                             blank=True,
                                             db_index=True)

    class Meta:
        ordering = ('number', )
        verbose_name = 'Базовый компонент рейтинга'
        verbose_name_plural = 'Базовые компоненты рейтинга'

    def __str__(self):
        string = (self._meta.verbose_name
                  + ' , id - {}, номер - {}'.format(self.id, self.number))
        if self.base_description:
            string += ', "{}"'.format(self.base_description[:80] + '...' if len(self.base_description) > 80 else self.base_description)
        return string

    @property
    def is_active(self):
        if not self.valid_to_year and not self.valid_to_month:
            return True
        else:
            if self.valid_to_month == 12:
                first_invalid_month = 1
                first_invalid_year = self.valid_to_year + 1
            else:
                first_invalid_month = self.valid_to_month + 1
                first_invalid_year = self.valid_to_year
            if datetime.date.today() >= datetime.date(year=first_invalid_year, month=first_invalid_month, day=1):
                return False
            else:
                return True

    def is_active_on_date(self, date):
        valid_from = datetime.date(year=self.valid_from_year, month=self.valid_from_month, day=1)
        if self.valid_to_year and self.valid_to_month:
            valid_to = datetime.date(year=self.valid_to_year, month=self.valid_to_month, day=1) - datetime.timedelta(days=1)
            return valid_from <= date <= valid_to
        else:
            return valid_from <= date


class MonthlyRatingComponent(models.Model):
    monthly_rating = models.ForeignKey(MonthlyRating,
                                       verbose_name=MonthlyRating._meta.verbose_name,
                                       on_delete=models.PROTECT,
                                       related_name='components')
    rating_component = models.ForeignKey(RatingComponent,
                                         verbose_name=RatingComponent._meta.verbose_name,
                                         on_delete=models.PROTECT,)
    responsible = models.ForeignKey(PrefectureEmployee,
                                    on_delete=models.SET_NULL,
                                    null=True,
                                    blank=True,
                                    verbose_name='Ответственный')
    additional_description = models.TextField(
        verbose_name='Дополнительное описание',
        blank=True,
        null=True
    )
    negotiator_comment = models.TextField(
        verbose_name='Комментарий согласовывающего',
        blank=True,
        null=True
    )
    region_comment = models.TextField(
        verbose_name='Комментарий района',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Компонент месячного рейтинга'
        verbose_name_plural = 'Компоненты месячного рейтинга'
        unique_together = ('monthly_rating', 'rating_component')

    def __str__(self):
        return self._meta.verbose_name + ' , id - {}'.format(self.id)

    @property
    def values(self) -> List[dict]:
        regions_ids = Region.objects.values_list('id')
        regions_dict = {region_id[0]: [] for region_id in regions_ids}
        for sub_component in self.related_sub_components.all():
            normalized_values = sub_component.get_normalized_values()
            for k, v in normalized_values:
                regions_dict[k].append(v)

        values_dict = {}
        for region_id in regions_dict:
            try:
                values_dict[region_id] = sum(regions_dict[region_id]) / self.related_sub_components.count()
            except ZeroDivisionError:
                values_dict[region_id] = None
        return_list = []
        for k, v in values_dict.items():
            dct = {
                "region_id": k,
                "value": v
            }
            return_list.append(dct)
        return return_list


class MonthlyRatingSubComponent(models.Model):
    BEST_TYPE_CHOICES = [
        (1, 'мин'),
        (2, 'макс'),
    ]
    monthly_rating_component = models.ForeignKey(
        MonthlyRatingComponent,
        on_delete=models.CASCADE,
        related_name='related_sub_components'
    )
    name = models.CharField(max_length=1000)
    date = models.DateField(null=True, blank=True)
    description = models.TextField()
    responsible = models.ForeignKey(PrefectureEmployee,
                                    on_delete=models.SET_NULL,
                                    blank=True,
                                    null=True)
    best_type = models.SmallIntegerField(choices=BEST_TYPE_CHOICES)
    document = models.FileField(upload_to='uploads/%Y/%m/%d/documents/')
    # regions = models.ManyToManyField(
    #     Region,
    #     through='MonthlyRatingSubComponentValue',
    #     related_name='monthly_rating_sub_components'
    # )

    class Meta:
        unique_together = ('name', 'date', )
        verbose_name = 'Подкомпонент месячного рейтинга'
        verbose_name_plural = 'Подкомпоненты месячных рейтингов'

    def __str__(self):
        return self._meta.verbose_name + ' , id - {}'.format(self.id)

    def get_flat_values(self):  # step 1
        flat_vales = {}
        for value in self.related_values:
            if value.is_average:
                flat_vales[value.region_id] = None
            elif not value.value:
                flat_vales[value.region_id] = 0
            else:
                flat_vales[value.region_id] = value.value
        values_without_none = [value for value in flat_vales.values() if value is not None]
        average = sum(values_without_none) / len(values_without_none)
        for k, v in flat_vales:
            if v is None:
                k[v] = average
        return flat_vales

    def get_abs_values(self):  # step 2
        pass

    def get_relative_values(self):  # step 3
        pass

    def get_normalized_values(self) -> Dict[int, Decimal]:  # step 4
        # !!! stub
        import random

        dct = {}
        for region in Region.objects.all():
            dct[region.id] = Decimal(str(random.randint / 100)[:4])
        return dct


class MonthlyRatingSubComponentValue(models.Model):
    region = models.ForeignKey(Region)
    monthly_rating_sub_component = models.ForeignKey(
        MonthlyRatingSubComponent,
        related_name='values',
        on_delete=models.CASCADE
    )
    is_average = models.BooleanField(default=False)
    value = models.DecimalField(max_digits=8,
                                decimal_places=2,
                                null=True,
                                blank=True)

    class Meta:
        unique_together = ('region', 'monthly_rating_sub_component')
        verbose_name = 'Значение подкомпонента месячного рейтинга'
        verbose_name_plural = 'Значения подкомпонентов месячных рейтингов'

    def __str__(self):
        return self._meta.verbose_name + ' , id - {}'.format(self.id)
