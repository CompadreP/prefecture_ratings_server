import datetime
from typing import Tuple, List

from decimal import Decimal
from django.db import models

from employees.models import PrefectureEmployee
from map.models import Region

YEAR_CHOICES = [(r, r) for r in
                range(2016, datetime.date.today().year + 1)]

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


BASE_DOCUMENT_CHOICES = [
    (1, 'Основной'),
    (2, 'Показатель'),
]


class SignerText(models.Model):
    text = models.CharField(max_length=100)


class BaseDocument(models.Model):
    kind = models.IntegerField(choices=BASE_DOCUMENT_CHOICES)
    description = models.TextField(unique=True)
    description_imp = models.TextField(unique=True)


class MonthlyRating(models.Model):
    base_document = models.ForeignKey(BaseDocument)
    is_negotiated = models.BooleanField(default=False,
                                        verbose_name='Согласован')
    is_approved = models.BooleanField(default=False,
                                      verbose_name='Утвержден')
    approved_by = models.ForeignKey(PrefectureEmployee,
                                    null=True,
                                    on_delete=models.SET_NULL)
    year = models.SmallIntegerField(verbose_name='Год',
                                    choices=YEAR_CHOICES,)
    month = models.SmallIntegerField(verbose_name='Месяц',
                                     choices=MONTH_CHOICES,)

    class Meta:
        unique_together = ('year', 'month')

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
    base_document = models.ForeignKey(BaseDocument)
    name = models.CharField(max_length=1000,
                            unique=True,
                            verbose_name='Наименование')
    responsible = models.ForeignKey(PrefectureEmployee,
                                    on_delete=models.SET_NULL,
                                    null=True,
                                    verbose_name='Ответственный')
    base_description = models.TextField(verbose_name='Базовое описание')
    weight = models.SmallIntegerField()
    valid_from_month = models.SmallIntegerField(verbose_name='Действует с месяца',
                                                choices=MONTH_CHOICES,
                                                db_index=True)
    valid_to_month = models.SmallIntegerField(verbose_name='Действует по месяц',
                                              choices=MONTH_CHOICES,
                                              null=True,
                                              blank=True,
                                              db_index=True)
    valid_from_year = models.SmallIntegerField(verbose_name='Действует с года',
                                               choices=YEAR_CHOICES,
                                               db_index=True)
    valid_to_year = models.SmallIntegerField(verbose_name='Действует по год',
                                             choices=YEAR_CHOICES,
                                             null=True,
                                             blank=True,
                                             db_index=True)

    class Meta:
        verbose_name = 'Базовый компонент рейтинга'
        verbose_name_plural = 'Базовые компоненты рейтинга'


class MonthlyRatingComponent(models.Model):
    # TODO create from RatingComponent on MonthlyRating approve
    rating_component = models.ForeignKey(RatingComponent,
                                         on_delete=models.CASCADE)
    additional_description = models.TextField(blank=True,
                                              null=True)
    negotiator_comment = models.TextField(blank=True,
                                          null=True)
    region_comment = models.TextField(blank=True,
                                      null=True)
    year = models.SmallIntegerField(verbose_name='Год',
                                    choices=YEAR_CHOICES,)
    month = models.SmallIntegerField(verbose_name='Месяц',
                                     choices=MONTH_CHOICES,)

    class Meta:
        verbose_name = 'Месячный компонент рейтинга'
        verbose_name_plural = 'Месячные компоненты рейтингов'
        unique_together = ('rating_component', 'year', 'month')
        index_together = ('year', 'month')
        ordering = ('-year', '-month')

    def get_values(self) -> dict:  # Region: Decimal
        # MONGO???
        pass

    def get_value_for_region(self, region: Region) -> Decimal:
        # TODO MEAT HERE
        pass

    # def save(self, *args, **kwargs):
    #     # TODO deny save if it is already approved
    #     pass

BEST_TYPE_CHOICES = [
    ('мин', 'мин'),
    ('макс', 'макс'),
]


class MonthlyRatingSubComponent(models.Model):
    monthly_rating_component = models.ForeignKey(MonthlyRatingComponent,
                                                 on_delete=models.CASCADE)
    name = models.CharField(max_length=1000)
    date = models.DateField(null=True, blank=True)
    description = models.TextField()
    responsible = models.ForeignKey(PrefectureEmployee,
                                    on_delete=models.SET_NULL,
                                    null=True)
    best_type = models.CharField(max_length=10,
                                 unique=True,
                                 choices=BEST_TYPE_CHOICES)
    document = models.FileField(upload_to='uploads/%Y/%m/%d/documents/')
    regions = models.ManyToManyField(
        Region,
        through='MonthlyRatingSubComponentValue',
        related_name='monthly_rating_sub_components'
    )

    def get_values(self) -> dict:  # Region: Decimal
        pass

    def get_value_for_region(self, region: Region) -> Decimal:
        pass

    # def save(self, *args, **kwargs):
    #     # May be calculate and put to mongo
    #     pass


class MonthlyRatingSubComponentValue(models.Model):
    region = models.ForeignKey(Region)
    monthly_rating_sub_component = models.ForeignKey(MonthlyRatingSubComponent)
    is_average = models.BooleanField(default=False)
    value = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        unique_together = ('region', 'monthly_rating_sub_component')
