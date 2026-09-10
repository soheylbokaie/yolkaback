from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    list_display = (
        "product",
        "user",
        "rating",
        "is_verified_purchase",
        "is_approved",
        "created_at",
    )

    list_filter = (
        "rating",
        "is_verified_purchase",
        "is_approved",
        "created_at",
    )

    search_fields = (
        "product__name",
        "product__sku",
        "user__email",
        "user__first_name",
        "user__last_name",
        "title",
        "comment",
    )

    autocomplete_fields = (
        "user",
        "product",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )
