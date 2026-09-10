from django.db import models


class Coupon(models.Model):

    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
    )

    description = models.TextField(
        blank=True,
    )

    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    fixed_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    minimum_order_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    usage_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    used_count = models.PositiveIntegerField(
        default=0,
    )

    starts_at = models.DateTimeField()

    expires_at = models.DateTimeField()

    is_active = models.BooleanField(
        default=True,
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"
        ordering = ["-created_at"]

    def __str__(self):
        return self.code
