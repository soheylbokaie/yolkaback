from rest_framework import serializers

from orders.models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "variant",
            "product_name",
            "sku",
            "quantity",
            "unit_price",
            "total_price",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "product_name",
            "sku",
            "unit_price",
            "total_price",
            "created_at",
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "status",
            "shipping_name",
            "shipping_phone",
            "shipping_province",
            "shipping_city",
            "shipping_address",
            "shipping_postal_code",
            "subtotal",
            "discount",
            "shipping_cost",
            "total",
            "coupon_code",
            "notes",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "order_number",
            "status",
            "subtotal",
            "discount",
            "shipping_cost",
            "total",
            "coupon_code",
            "created_at",
            "updated_at",
        ]
