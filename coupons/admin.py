from django.contrib import admin

from .models import Coupon


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):

    list_display = (
        "code",
        "percentage",
        "fixed_amount",
        "minimum_order_amount",
        "used_count",
        "usage_limit",
        "starts_at",
        "expires_at",
        "is_active",
    )

    list_filter = (
        "is_active",
        "starts_at",
        "expires_at",
    )

    search_fields = (
        "code",
        "description",
    )

    readonly_fields = (
        "used_count",
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)
