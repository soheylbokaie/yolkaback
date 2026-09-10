from django.conf import settings
from django.db import models

from catalog.models import Product


class Review(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    rating = models.PositiveSmallIntegerField()

    title = models.CharField(
        max_length=255,
        blank=True,
    )

    comment = models.TextField()

    is_verified_purchase = models.BooleanField(
        default=False,
    )

    is_approved = models.BooleanField(
        default=False,
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_user_product_review",
            )
        ]

    def __str__(self):
        return f"{self.product.name} - {self.rating}/5"
