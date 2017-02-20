from ratings.views import RatingsViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'monthly/', RatingsViewSet)
urlpatterns = router.urls
