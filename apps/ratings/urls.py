from rest_framework.routers import DefaultRouter

from apps.ratings.views import MonthlyRatingsViewSet, \
    MonthlyRatingElementsViewSet, MonthlyRatingSubElementsViewSet

urlpatterns = []

router = DefaultRouter()
router.register(r'monthly/sub_elements', MonthlyRatingSubElementsViewSet)
urlpatterns += router.urls

router = DefaultRouter()
router.register(r'monthly/elements', MonthlyRatingElementsViewSet)
urlpatterns += router.urls

router = DefaultRouter()
router.register(r'monthly', MonthlyRatingsViewSet)
urlpatterns += router.urls





