from ratings.views import MonthlyRatingsViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'monthly/', MonthlyRatingsViewSet)
urlpatterns = router.urls


