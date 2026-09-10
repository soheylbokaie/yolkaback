from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(
        max_length=150,
        unique=True,
    )

    slug = models.SlugField(
        max_length=180,
        unique=True,
        db_index=True,
        blank=True,
    )

    description = models.TextField(
        blank=True,
    )

    image = models.ImageField(
        upload_to="categories/",
        blank=True,
        null=True,
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )

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
        ordering = ["name"]
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
    )

    name = models.CharField(
        max_length=255,
    )

    slug = models.SlugField(
        max_length=280,
        unique=True,
        db_index=True,
        blank=True,
    )

    sku = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
    )

    short_description = models.CharField(
        max_length=500,
        blank=True,
    )

    description = models.TextField(
        blank=True,
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    compare_at_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    cost_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    stock = models.PositiveIntegerField(
        default=0,
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
    )

    is_featured = models.BooleanField(
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
        ordering = ["-created_at"]
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    @property
    def is_in_stock(self):
        return self.stock > 0

    @property
    def discount_percentage(self):
        if not self.compare_at_price:
            return 0

        if self.compare_at_price <= self.price:
            return 0

        return round(
            ((self.compare_at_price - self.price) / self.compare_at_price) * 100
        )

    def __str__(self):
        return self.name


class ProductImage(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
    )

    image = models.ImageField(
        upload_to="products/",
    )

    alt_text = models.CharField(
        max_length=255,
        blank=True,
    )

    is_primary = models.BooleanField(
        default=False,
    )

    sort_order = models.PositiveIntegerField(
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"

    def __str__(self):
        return f"{self.product.name} image"


class ProductVariant(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants",
    )

    name = models.CharField(
        max_length=255,
    )

    sku = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    stock = models.PositiveIntegerField(
        default=0,
    )

    attributes = models.JSONField(
        default=dict,
        blank=True,
    )

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
        ordering = ["product", "name"]
        verbose_name = "Product Variant"
        verbose_name_plural = "Product Variants"

    def __str__(self):
        return f"{self.product.name} - {self.name}"
