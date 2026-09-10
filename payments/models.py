from django.db import models

from orders.models import Order


class Payment(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"
        REFUNDED = "refunded", "Refunded"

    class Method(models.TextChoices):
        CARD = "card", "Card"
        BANK_TRANSFER = "bank_transfer", "Bank Transfer"
        CASH_ON_DELIVERY = "cash_on_delivery", "Cash on Delivery"

    order = models.OneToOneField(
        Order,
        on_delete=models.PROTECT,
        related_name="payment",
    )

    transaction_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
    )

    authority = models.CharField(
        max_length=255,
        blank=True,
    )

    method = models.CharField(
        max_length=30,
        choices=Method.choices,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    gateway_response = models.JSONField(
        default=dict,
        blank=True,
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment - {self.order.order_number}"
