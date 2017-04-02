from typing import List

from django.core.cache import cache


def invalidate_caches(keys: List[str]) -> None:
    for key in keys:
        cache.delete(key)
