from rest_framework import serializers

from catalog.models import (
    Category,
    Product,
    ProductImage,
    ProductVariant,
)


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = [
            "id",
            "image",
            "alt_text",
            "is_primary",
            "sort_order",
        ]


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = [
            "id",
            "name",
            "sku",
            "price",
            "stock",
            "attributes",
            "is_active",
        ]


class CategorySerializer(serializers.ModelSerializer):
    children_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "image",
            "parent",
            "is_active",
            "children_count",
            "created_at",
            "updated_at",
        ]

    def get_children_count(self, obj):
        return obj.children.count()


class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()
    discount_percentage = serializers.ReadOnlyField()
    is_in_stock = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "sku",
            "short_description",
            "price",
            "compare_at_price",
            "stock",
            "discount_percentage",
            "is_in_stock",
            "is_active",
            "is_featured",
            "category",
            "primary_image",
            "created_at",
        ]

    def get_primary_image(self, obj):
        image = obj.images.filter(is_primary=True).first()

        if not image:
            image = obj.images.first()

        if not image:
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(image.image.url)

        return image.image.url


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)

    discount_percentage = serializers.ReadOnlyField()
    is_in_stock = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "sku",
            "short_description",
            "description",
            "price",
            "compare_at_price",
            "cost_price",
            "stock",
            "discount_percentage",
            "is_in_stock",
            "is_active",
            "is_featured",
            "category",
            "images",
            "variants",
            "created_at",
            "updated_at",
        ]
