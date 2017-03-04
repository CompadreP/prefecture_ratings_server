from rest_framework.routers import DefaultRouter

from apps.ratings.views import MonthlyRatingsViewSet, \
    MonthlyRatingComponentsViewSet, MonthlyRatingSubComponentsViewSet

urlpatterns = []

router = DefaultRouter()
router.register(r'monthly/sub_components', MonthlyRatingSubComponentsViewSet)
urlpatterns += router.urls

router = DefaultRouter()
router.register(r'monthly/components', MonthlyRatingComponentsViewSet)
urlpatterns += router.urls

router = DefaultRouter()
router.register(r'monthly', MonthlyRatingsViewSet)
urlpatterns += router.urls





