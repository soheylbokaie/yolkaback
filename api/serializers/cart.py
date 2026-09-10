from rest_framework import serializers

from cart.models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
    )

    product_price = serializers.DecimalField(
        source="product.price",
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    product_image = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_price",
            "product_image",
            "variant",
            "quantity",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def get_product_image(self, obj):
        image = obj.product.images.filter(is_primary=True).first()

        if not image:
            image = obj.product.images.first()

        if not image:
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(image.image.url)

        return image.image.url


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(
        many=True,
        read_only=True,
    )

    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            "id",
            "items",
            "total_items",
            "created_at",
            "updated_at",
        ]

    def get_total_items(self, obj):
        return sum(item.quantity for item in obj.items.all())
