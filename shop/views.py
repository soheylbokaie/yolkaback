from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, ConsultRequest, Order, Product, Wood
from .serializers import (
    CategorySerializer,
    ConsultRequestSerializer,
    OrderSerializer,
    ProductSerializer,
    WoodSerializer,
)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """لیست و جزئیات محصولات فعال، با فیلتر دسته‌بندی و جست‌وجو."""

    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True).select_related("category", "wood")
        category = self.request.query_params.get("category")
        if category and category != "all":
            qs = qs.filter(category__slug=category)
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(title__icontains=search)
        if self.request.query_params.get("in_stock") == "1":
            qs = qs.filter(stock__gt=0)
        return qs


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class WoodListView(generics.ListAPIView):
    queryset = Wood.objects.all()
    serializer_class = WoodSerializer
    permission_classes = [AllowAny]


class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]


class ConsultCreateView(generics.CreateAPIView):
    queryset = ConsultRequest.objects.all()
    serializer_class = ConsultRequestSerializer
    permission_classes = [AllowAny]


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "ok", "brand": "Yolka Wood"})
