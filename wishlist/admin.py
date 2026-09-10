from django.contrib import admin

from .models import Wishlist


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "product",
        "created_at",
    )

    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
        "product__name",
        "product__sku",
    )

    autocomplete_fields = (
        "user",
        "product",
    )

    list_filter = (
        "created_at",
    )