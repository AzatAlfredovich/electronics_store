from django.urls import include, path
from rest_framework.routers import DefaultRouter

from electronics.views import NetworkNodeViewSet

router = DefaultRouter()

router.register("network-nodes", NetworkNodeViewSet, basename="network-nodes")

urlpatterns = [
    path("", include(router.urls)),
]
