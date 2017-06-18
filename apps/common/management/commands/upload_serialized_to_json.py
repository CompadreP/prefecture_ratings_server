import simplejson as json

import psycopg2
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from apps.ratings.models import MonthlyRating, MonthlyRatingElement
from apps.ratings.serializers import MonthlyRatingDetailSerializer, \
    MonthlyRatingElementDetailFullSerializer
from apps.ratings.utils import put_approved_rating_in_json, \
    put_approved_rating_element_in_json


class Command(BaseCommand):
    def handle(self, *args, **options):
        conn = psycopg2.connect(
            database=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT'],
        )
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE _ratings_json (
              id NUMERIC PRIMARY KEY,
              data JSONB
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE _ratings_elements_json (
              id NUMERIC PRIMARY KEY,
              data JSONB
            );
            """
        )
        for rating in MonthlyRating.objects.filter(is_approved=True):
            put_approved_rating_in_json(rating, conn)
        for rating_element in (
                MonthlyRatingElement
                    .objects
                    .filter(monthly_rating__is_approved=True)
        ):
            put_approved_rating_element_in_json(rating_element, conn)
        conn.commit()
        print('Success!')
