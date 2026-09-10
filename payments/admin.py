from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        "order",
        "amount",
        "method",
        "status",
        "transaction_id",
        "paid_at",
        "created_at",
    )

    list_filter = (
        "status",
        "method",
        "paid_at",
        "created_at",
    )

    search_fields = (
        "order__order_number",
        "transaction_id",
        "authority",
        "order__user__email",
    )

    autocomplete_fields = ("order",)

    readonly_fields = (
        "created_at",
        "updated_at",
        "paid_at",
    )

    date_hierarchy = "created_at"
