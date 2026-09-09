from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryListView,
    ConsultCreateView,
    HealthView,
    OrderCreateView,
    ProductViewSet,
    WoodListView,
)
from django.http import JsonResponse
from django.urls import path, include


def health(request):
    return JsonResponse({"status": "ok", "message": "Yolka API is running"})


router = DefaultRouter()
router.register("products", ProductViewSet, basename="product")

urlpatterns = [
    path("", health),
    path("", include(router.urls)),
    path("categories/", CategoryListView.as_view(), name="categories"),
    path("woods/", WoodListView.as_view(), name="woods"),
    path("orders/", OrderCreateView.as_view(), name="order-create"),
    path("consults/", ConsultCreateView.as_view(), name="consult-create"),
    path("health/", HealthView.as_view(), name="health"),
]
