from django.conf import settings
from django.db import models

from catalog.models import Product


class Wishlist(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="wishlists",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Wishlist Item"
        verbose_name_plural = "Wishlist Items"

        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_user_product_wishlist",
            )
        ]

    def __str__(self):
        return f"{self.user.email} - {self.product.name}"
