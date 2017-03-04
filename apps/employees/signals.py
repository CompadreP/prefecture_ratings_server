from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import PrefectureEmployee, RegionEmployee


def delete_corresponding_user(**kwargs):
    kwargs['instance'].user.delete()


@receiver(post_delete, sender=PrefectureEmployee)
def delete_prefecture_employee_corresponding_user(sender, **kwargs):
    delete_corresponding_user(**kwargs)


@receiver(post_delete, sender=RegionEmployee)
def delete_region_employee_corresponding_user(sender, **kwargs):
    delete_corresponding_user(**kwargs)
