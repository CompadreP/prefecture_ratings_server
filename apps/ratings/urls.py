from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from apps.ratings.views import MonthlyRatingsViewSet, \
    MonthlyRatingElementsViewSet, MonthlyRatingSubElementsViewSet, \
    DownloadRatingAPIView

urlpatterns = [
    url(r'^downloads/(?P<year>\d{4})/(?P<month>\d{1,2})/',
        DownloadRatingAPIView.as_view(),
        name='rating_download'),
]

router = DefaultRouter()
router.register(r'monthly/sub_elements', MonthlyRatingSubElementsViewSet)
urlpatterns += router.urls

router = DefaultRouter()
router.register(r'monthly/elements', MonthlyRatingElementsViewSet)
urlpatterns += router.urls

router = DefaultRouter()
router.register(r'monthly', MonthlyRatingsViewSet)
urlpatterns += router.urls





