from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

    fields = (
        "product",
        "variant",
        "product_name",
        "sku",
        "quantity",
        "unit_price",
        "total_price",
    )

    readonly_fields = (
        "product_name",
        "sku",
        "unit_price",
        "total_price",
    )

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for item in instances:
            if not item.product:
                continue

            product = item.product
            variant = item.variant

            # Product information
            item.product_name = product.name

            # Variant SKU or product SKU
            if variant:
                item.sku = variant.sku
            else:
                item.sku = product.sku

            # Get price
            if variant:
                item.unit_price = variant.price
            else:
                item.unit_price = product.price

            # Calculate total
            item.total_price = item.unit_price * item.quantity

            item.save()

        formset.save_m2m()


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "order_number",
        "user",
        "address",
        "status",
        "subtotal",
        "discount",
        "shipping_cost",
        "total",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "order_number",
        "user__username",
        "user__email",
        "address__city",
        "address__province",
        "address__postal_code",
    )

    readonly_fields = (
        "order_number",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Order Information",
            {
                "fields": (
                    "order_number",
                    "user",
                    "address",
                    "status",
                )
            },
        ),
        (
            "Pricing",
            {
                "fields": (
                    "subtotal",
                    "discount",
                    "shipping_cost",
                    "total",
                    "coupon_code",
                )
            },
        ),
        (
            "Additional Information",
            {
                "fields": (
                    "notes",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    inlines = [
        OrderItemInline,
    ]
