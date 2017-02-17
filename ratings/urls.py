from ratings.views import RatingsViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', RatingsViewSet)
urlpatterns = router.urls
