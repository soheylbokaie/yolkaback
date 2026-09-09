from django.db import transaction
from rest_framework import serializers

from .models import Category, ConsultRequest, Order, OrderItem, Product, Wood


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "slug", "name"]


class WoodSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Wood
        fields = ["id", "slug", "name_fa", "name_en", "texture", "description", "image"]

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return obj.image_url


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field="slug", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    wood = serializers.CharField(source="wood.name_fa", read_only=True)
    image = serializers.SerializerMethodField()
    in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "slug", "title", "description", "category", "category_name",
            "wood", "price", "old_price", "badge", "stock", "in_stock",
            "image", "alt",
        ]

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return obj.image_url


class OrderItemInputSerializer(serializers.Serializer):
    product = serializers.SlugRelatedField(
        slug_field="slug", queryset=Product.objects.filter(is_active=True)
    )
    quantity = serializers.IntegerField(min_value=1, max_value=99)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemInputSerializer(many=True, write_only=True)
    total = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = ["id", "full_name", "phone", "address", "note", "items", "total", "status", "created_at"]
        read_only_fields = ["status", "created_at"]

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("سبد خرید خالی است.")
        for row in value:
            product = row["product"]
            if product.stock < row["quantity"]:
                raise serializers.ValidationError(
                    f"موجودی «{product.title}» کافی نیست (موجودی: {product.stock})."
                )
        return value

    @transaction.atomic
    def create(self, validated_data):
        items = validated_data.pop("items")
        order = Order.objects.create(**validated_data)
        for row in items:
            product = row["product"]
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=row["quantity"],
                unit_price=product.price,
            )
            product.stock -= row["quantity"]
            product.save(update_fields=["stock"])
        order.recalculate()
        order.save(update_fields=["total"])
        return order


class ConsultRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultRequest
        fields = ["id", "full_name", "phone", "message", "created_at"]
        read_only_fields = ["created_at"]
