from django.contrib import admin

from .models import (
    Category,
    Product,
    ProductImage,
    ProductVariant,
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage

    extra = 1

    fields = (
        "image",
        "alt_text",
        "is_primary",
        "sort_order",
    )


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant

    extra = 1

    fields = (
        "name",
        "sku",
        "price",
        "stock",
        "attributes",
        "is_active",
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "parent",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
        "parent",
        "created_at",
    )

    search_fields = (
        "name",
        "slug",
        "description",
    )

    autocomplete_fields = ("parent",)

    prepopulated_fields = {
        "slug": ("name",),
    }

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "sku",
        "category",
        "price",
        "stock",
        "is_active",
        "is_featured",
        "created_at",
    )

    list_filter = (
        "category",
        "is_active",
        "is_featured",
        "created_at",
    )

    search_fields = (
        "name",
        "sku",
        "slug",
        "description",
    )

    autocomplete_fields = ("category",)

    prepopulated_fields = {
        "slug": ("name",),
    }

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_per_page = 50

    inlines = (
        ProductImageInline,
        ProductVariantInline,
    )

    fieldsets = (
        (
            "Product",
            {
                "fields": (
                    "name",
                    "slug",
                    "sku",
                    "category",
                )
            },
        ),
        (
            "Description",
            {
                "fields": (
                    "short_description",
                    "description",
                )
            },
        ),
        (
            "Pricing",
            {
                "fields": (
                    "price",
                    "compare_at_price",
                    "cost_price",
                )
            },
        ),
        (
            "Inventory",
            {"fields": ("stock",)},
        ),
        (
            "Visibility",
            {
                "fields": (
                    "is_active",
                    "is_featured",
                )
            },
        ),
        (
            "Dates",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):

    list_display = (
        "product",
        "is_primary",
        "sort_order",
        "created_at",
    )

    list_filter = ("is_primary",)

    search_fields = (
        "product__name",
        "product__sku",
        "alt_text",
    )

    autocomplete_fields = ("product",)

    ordering = (
        "product",
        "sort_order",
    )


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "product",
        "sku",
        "price",
        "stock",
        "is_active",
    )

    list_filter = ("is_active",)

    search_fields = (
        "name",
        "sku",
        "product__name",
    )

    autocomplete_fields = ("product",)
