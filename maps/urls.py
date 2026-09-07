from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MapRegionViewSet

router = DefaultRouter()
router.register(r"regions", MapRegionViewSet, basename="map-region")
urlpatterns = [
    path("", include(router.urls)),
]
