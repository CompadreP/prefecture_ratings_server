import datetime
from typing import List, Dict

from django.conf import settings
from django.db import models

from pymongo import MongoClient

from apps.employees.models import PrefectureEmployee, RatingsUser
from apps.map.models import Region
from apps.ratings.serializers import MonthlyRatingDetailSerializer, \
    MonthlyRatingElementDetailFullSerializer
from apps.ratings.tasks import send_emails

YEAR_CHOICES = [(r, r) for r in
                range(2016, datetime.date.today().year + 2)]

MONTHS = {
    1: 'Январь',
    2: 'Февраль',
    3: 'Март',
    4: 'Апрель',
    5: 'Май',
    6: 'Июнь',
    7: 'Июль',
    8: 'Август',
    9: 'Сентябрь',
    10: 'Октябрь',
    11: 'Ноябрь',
    12: 'Декабрь',
}


MONTH_CHOICES = list(MONTHS.items())

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
    kind = models.IntegerField(verbose_name='Тип документа',
                               choices=BASE_DOCUMENT_CHOICES)
    description = models.TextField(verbose_name='Наименование', unique=True)
    description_imp = models.TextField(
        verbose_name='Наименование (повелительное)', unique=True)

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
                                    choices=YEAR_CHOICES, )
    month = models.SmallIntegerField(verbose_name='Месяц',
                                     choices=MONTH_CHOICES, )
    signer_text = models.ForeignKey(
        SignerText,
        verbose_name=SignerText._meta.verbose_name,
        on_delete=models.PROTECT
    )
    generated_excel = models.FileField(
        null=True,
        blank=True
    )

    class Meta:
        unique_together = ('year', 'month')
        ordering = ('-year', '-month')
        verbose_name = 'Месячный рейтинг'
        verbose_name_plural = 'Месячные рейтинги'

    def __str__(self):
        return 'Год - {}, месяц - {}'.format(self.year, self.month)

    @staticmethod
    def cache_key_prefix():
        return 'monthly_rating_'

    negotiaied_subject = 'Рейтинг районов за {month} {year} года согласован.'
    negotiaied_body = 'Ознакомиться с текущими результатами можно по ссылке - ' \
                      '\n https://prefecture-ratings.ru/rating/{id}'

    def negotiate(self):
        self.is_negotiated = True
        self.save()
        emails = [email[0]
                  for email
                  in RatingsUser.objects.filter(is_active=True).values_list('email')]
        send_emails.apply_async(args=(
            emails,
            self.negotiaied_subject.format(
                month=self.month,
                year=self.year
            ),
            self.negotiaied_body.format(self.id)
        ))

    approved_subject = 'Рейтинг районов за {month} {year} года утвержден.'
    approved_body = 'Ознакомиться с финальными результатами можно по ссылке - ' \
                    '\n https://prefecture-ratings.ru/rating/{id}'

    def approve(self, user=None):
        # TODO on approve save to mongo fully serialized, generate excel and send emails
        self.is_approved = True

        client = MongoClient(settings.MONGODB['HOST'], settings.MONGODB['PORT'])
        db = client.ratings
        mongo_ratings = db.monthly_ratings
        # creating index if it's not created
        rating_name = 'monthly_rating'
        rating_element_name = 'monthly_rating_element'
        if rating_name not in mongo_ratings.index_information():
            mongo_ratings.create_index(rating_name, unique=True)
        if rating_element_name not in mongo_ratings.index_information():
            mongo_ratings.create_index(rating_element_name, unique=True)
        mongo_ratings.insert_one(MonthlyRatingDetailSerializer(self))
        mongo_rating_elements = db.monthly_rating_elements
        elements = MonthlyRatingElementDetailFullSerializer(
            self.elements,
            many=True,
            context={'options': ['include_sub_elements']},
        )
        mongo_rating_elements.insert_many(elements)
        self.save()
        emails = [email[0]
                  for email
                  in RatingsUser.objects.filter(is_active=True).values_list('email')]
        send_emails.apply_async(args=(
            emails,
            self.approved_subject.format(
                month=self.month,
                year=self.year
            ),
            self.approved_body.format(self.id)
        ))


class RatingElement(models.Model):
    WEIGHT_CHOICES = [(r, r) for r in
                      range(1, 11)]
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
    responsible = models.ForeignKey(PrefectureEmployee,
                                    on_delete=models.SET_NULL,
                                    null=True,
                                    blank=True,
                                    verbose_name='Ответственный (базовый)')
    valid_from_month = models.SmallIntegerField(
        verbose_name='Действует с месяца',
        choices=MONTH_CHOICES,
        db_index=True)
    valid_from_year = models.SmallIntegerField(verbose_name='Действует с года',
                                               choices=YEAR_CHOICES,
                                               db_index=True)
    valid_to_month = models.SmallIntegerField(
        verbose_name='Действует по месяц(включительно)',
        choices=MONTH_CHOICES,
        null=True,
        blank=True,
        db_index=True)
    valid_to_year = models.SmallIntegerField(
        verbose_name='Действует по год(включительно)',
        choices=YEAR_CHOICES,
        null=True,
        blank=True,
        db_index=True)

    class Meta:
        ordering = ('id', )
        verbose_name = 'Базовый компонент рейтинга'
        verbose_name_plural = 'Базовые компоненты рейтинга'

    def __str__(self):
        string = (self._meta.verbose_name
                  + ' , id - {}'.format(self.id))
        if self.base_description:
            string += ', "{}"'.format(
                self.base_description[:80] + '...' if len(
                    self.base_description) > 80 else self.base_description)
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
            if datetime.date.today() >= datetime.date(year=first_invalid_year,
                                                      month=first_invalid_month,
                                                      day=1):
                return False
            else:
                return True

    def is_active_on_date(self, date: datetime.date) -> bool:
        valid_from = datetime.date(year=self.valid_from_year,
                                   month=self.valid_from_month, day=1)
        if self.valid_to_year and self.valid_to_month:
            valid_to = datetime.date(year=self.valid_to_year,
                                     month=self.valid_to_month,
                                     day=1) - datetime.timedelta(days=1)
            return valid_from <= date <= valid_to
        else:
            return valid_from <= date


BEST_TYPE_CHOICES = [
    (1, 'мин'),
    (2, 'макс'),
]


class MonthlyRatingElement(models.Model):
    monthly_rating = models.ForeignKey(
        MonthlyRating,
        verbose_name=MonthlyRating._meta.verbose_name,
        on_delete=models.PROTECT,
        related_name='elements'
    )
    rating_element = models.ForeignKey(
        RatingElement,
        verbose_name=RatingElement._meta.verbose_name,
        on_delete=models.PROTECT,
    )
    number = models.PositiveIntegerField(verbose_name='№ п/п', null=True)
    responsible = models.ForeignKey(
        PrefectureEmployee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Ответственный'
    )
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
    best_type = models.SmallIntegerField(choices=BEST_TYPE_CHOICES, null=True)

    class Meta:
        ordering = ('number', 'id',)
        verbose_name = 'Компонент месячного рейтинга'
        verbose_name_plural = 'Компоненты месячного рейтинга'
        unique_together = ('monthly_rating', 'rating_element')

    def __str__(self):
        return self._meta.verbose_name + \
               ' , id - {}, номер - {}'.format(self.id, self.number)

    @staticmethod
    def cache_key_prefix():
        return 'monthly_rating_element_'

    @property
    def values(self) -> Dict:
        regions_ids = Region.objects.values_list('id')
        regions_dict = {region_id[0]: None
                        for region_id
                        in regions_ids}
        values_array = []
        for sub_element in self.related_sub_elements.all():
            values_array.append(sub_element.get_normalized_values())
        for sub_element_dict in values_array:
            for region_id, value in sub_element_dict.items():
                if regions_dict[region_id] is not None and value is not None:
                    regions_dict[region_id] += value
                elif regions_dict[region_id] is None and value is not None:
                    regions_dict[region_id] = value
        values_len = len(values_array)
        if values_len != 0:
            for region in regions_dict:
                if regions_dict[region] is not None:
                    regions_dict[region] /= values_len
        return regions_dict


class MonthlyRatingSubElement(models.Model):
    DISPLAY_TYPE_CHOICES = [
        (1, 'десятичное число'),
        (2, 'процент'),
    ]
    monthly_rating_element = models.ForeignKey(
        MonthlyRatingElement,
        on_delete=models.CASCADE,
        related_name='related_sub_elements'
    )
    name = models.CharField(max_length=1000)
    date = models.DateField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    responsible = models.ForeignKey(PrefectureEmployee,
                                    on_delete=models.SET_NULL,
                                    blank=True,
                                    null=True)
    best_type = models.SmallIntegerField(choices=BEST_TYPE_CHOICES)
    document = models.FileField(
        upload_to='uploads/%Y/%m/%d/documents/',
        null=True,
        blank=True
    )
    display_type = models.SmallIntegerField(choices=DISPLAY_TYPE_CHOICES,
                                            default=1)

    class Meta:
        unique_together = ('name', 'date',)
        ordering = ('id',)
        verbose_name = 'Подкомпонент месячного рейтинга'
        verbose_name_plural = 'Подкомпоненты месячных рейтингов'

    def __str__(self):
        return self._meta.verbose_name + ' , id - {}'.format(self.id)

    def get_min_value(self, lst: List, idx: int) -> float:
        min_value = None
        for value in lst:
            if value[idx] is not None \
                    and (min_value is None or value[idx] < min_value):
                min_value = value[idx]
        return min_value

    def get_avg_value(self, lst: List, idx: int) -> float:
        lst = [x for x in lst if x[idx] is not None]
        if lst:
            sum_value = 0
            for value in lst:
                if value[idx] is not None:
                    sum_value += value[idx]
            return sum_value / len(lst)

    def get_max_value(self, lst: List, idx) -> float:
        max_value = None
        for value in lst:
            if value[idx] is not None \
                    and (max_value is None or value[idx] > max_value):
                max_value = value[idx]
        return max_value

    def get_non_negative_values(self) -> List[List]:  # step 1
        extracted_values = \
                [list(value)
                 for value
                 in self.values.values_list('region', 'is_average', 'value')]
        avg_value = self.get_avg_value(extracted_values, 2) or 0
        min_value = self.get_min_value(extracted_values, 2) or 0
        for value in extracted_values:
            if value[1]:
                value[2] = avg_value
            if value[2] is not None and min_value < 0:
                value[2] += abs(min_value)
            del value[1]
        return extracted_values

    def get_relative_values(self) -> List[List]:  # step 2
        extracted_values = self.get_non_negative_values()
        if self.best_type == 1:
            min_value = self.get_min_value(extracted_values, 1)
            if min_value != 0:
                for value in extracted_values:
                    if value[1] is not None:
                        value[1] /= min_value
        elif self.best_type == 2:
            max_value = self.get_max_value(extracted_values, 1)
            if max_value != 0:
                for value in extracted_values:
                    if value[1] is not None:
                        value[1] /= max_value
        return extracted_values

    def get_normalized_values(self) -> Dict:  # step 3
        extracted_values = self.get_relative_values()
        min_value = self.get_min_value(extracted_values, 1)
        max_value = self.get_max_value(extracted_values, 1)
        for value in extracted_values:
            if min_value == max_value:
                value[1] = 1
            elif self.best_type == 1 and value[1] is not None:
                value[1] = (value[1] - max_value) / (min_value - max_value)
            elif self.best_type == 2 and value[1] is not None:
                value[1] = (value[1] - min_value) / (max_value - min_value)
        normalized_values = {value[0]: value[1]
                             for value
                             in extracted_values}
        return normalized_values


class MonthlyRatingSubElementValue(models.Model):
    region = models.ForeignKey(Region)
    monthly_rating_sub_element = models.ForeignKey(
        MonthlyRatingSubElement,
        related_name='values',
        on_delete=models.CASCADE
    )
    is_average = models.BooleanField(default=False)
    value = models.DecimalField(max_digits=8,
                                decimal_places=5,
                                null=True,
                                blank=True)

    class Meta:
        unique_together = ('region', 'monthly_rating_sub_element')
        ordering = ('id', )
        verbose_name = 'Значение подкомпонента месячного рейтинга'
        verbose_name_plural = 'Значения подкомпонентов месячных рейтингов'

    def __str__(self):
        return self._meta.verbose_name + ' , id - {}'.format(self.id)
