from rest_framework.routers import DefaultRouter

from map.views import RegionsViewSet

router = DefaultRouter()
router.register(r'regions', RegionsViewSet)
urlpatterns = router.urls


