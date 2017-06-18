import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.ratings.models import MonthlyRating
from apps.ratings.utils import MonthlyRatingExcelGenerator


class Command(BaseCommand):
    def handle(self, *args, **options):
        for rating in MonthlyRating.objects.filter(is_approved=True):
            gen = MonthlyRatingExcelGenerator(rating)
            wb = gen.generate()
            file_name = 'Rating_{}_{}.xlsx'.format(
                rating.year,
                rating.month
            )
            wb.save(os.path.join(settings.PUBLIC_DIR, file_name))
        print('Success!')
