import datetime
from typing import Tuple, List

from decimal import Decimal
from django.db import models

from employees.models import RegionEmployee, PrefectureEmployee
from map.models import Region

YEAR_CHOICES = [(r, r) for r in
                range(2015, datetime.date.today().year + 1)]

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


class MonthlyRating(models.Model):
    # TODO Should be saved with related instances versions at the time of
    # saving
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


class RatingComponent(models.Model):
    name = models.CharField(max_length=1000, unique=True)
    responsible = models.ForeignKey(PrefectureEmployee,
                                    on_delete=models.SET_NULL,
                                    null=True)
    description = models.TextField()
    valid_from_year = models.SmallIntegerField(verbose_name='Год',
                                               choices=YEAR_CHOICES,
                                               db_index=True)
    valid_to_year = models.SmallIntegerField(verbose_name='Год',
                                             choices=YEAR_CHOICES,
                                             null=True,
                                             blank=True,
                                             db_index=True)
    valid_from_month = models.SmallIntegerField(verbose_name='Год',
                                                choices=MONTH_CHOICES,
                                                db_index=True)
    valid_to_month = models.SmallIntegerField(verbose_name='Год',
                                              choices=MONTH_CHOICES,
                                              null=True,
                                              blank=True,
                                              db_index=True)

    class Meta:
        verbose_name = ''
        verbose_name_plural = ''


class MonthlyRatingComponent(models.Model):
    # TODO create from RatingComponent on MonthlyRating approve
    rating_component = models.ForeignKey(RatingComponent,
                                         on_delete=models.CASCADE)
    additional_description = models.TextField(blank=True,
                                              null=True)
    negotiator_comment = models.TextField(blank=True,
                                          null=True)
    year = models.SmallIntegerField(verbose_name='Год',
                                    choices=YEAR_CHOICES,)
    month = models.SmallIntegerField(verbose_name='Месяц',
                                     choices=MONTH_CHOICES,)

    class Meta:
        unique_together = ('rating_component', 'year', 'month')
        index_together = ('year', 'month')

    def get_values(self) -> dict:  # Region: Decimal
        pass

    def get_value_for_region(self, region: Region) -> Decimal:
        pass


class MonthlyRatingSubComponent(models.Model):
    monthly_rating_component = models.ForeignKey(MonthlyRatingComponent,
                                                 on_delete=models.CASCADE)
    name = models.CharField(max_length=1000)
    date = models.DateField(null=True, blank=True)
    description = models.TextField()
    responsible = models.ForeignKey(PrefectureEmployee,
                                    on_delete=models.SET_NULL,
                                    null=True)
