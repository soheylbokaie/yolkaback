from django.contrib import admin

from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem

    extra = 0

    fields = (
        "product",
        "variant",
        "quantity",
        "created_at",
    )

    readonly_fields = ("created_at",)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "total_items",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
    )

    autocomplete_fields = ("user",)

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    inlines = (CartItemInline,)

    @admin.display(description="Items")
    def total_items(self, obj):
        return sum(item.quantity for item in obj.items.all())


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):

    list_display = (
        "cart",
        "product",
        "variant",
        "quantity",
        "created_at",
    )

    search_fields = (
        "cart__user__email",
        "product__name",
        "product__sku",
    )

    autocomplete_fields = (
        "cart",
        "product",
        "variant",
    )
