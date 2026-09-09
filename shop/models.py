from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    slug = models.SlugField("شناسه", max_length=60, unique=True)
    name = models.CharField("نام دسته", max_length=80)
    order = models.PositiveSmallIntegerField("ترتیب", default=0)

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ["order", "id"]

    def __str__(self):
        return self.name


class Wood(models.Model):
    slug = models.SlugField("شناسه", max_length=60, unique=True)
    name_fa = models.CharField("نام فارسی", max_length=60)
    name_en = models.CharField("نام لاتین", max_length=60)
    texture = models.CharField("بافت", max_length=120, blank=True)
    description = models.TextField("توضیح", blank=True)
    image = models.ImageField("تصویر بافت", upload_to="woods/", blank=True, null=True)
    image_url = models.CharField("آدرس تصویر", max_length=300, blank=True)

    class Meta:
        verbose_name = "نوع چوب"
        verbose_name_plural = "انواع چوب"
        ordering = ["id"]

    def __str__(self):
        return self.name_fa


class Product(models.Model):
    slug = models.SlugField("شناسه", max_length=120, unique=True, blank=True)
    title = models.CharField("عنوان", max_length=140)
    description = models.TextField("توضیح کوتاه", blank=True)
    category = models.ForeignKey(
        Category, verbose_name="دسته‌بندی", related_name="products", on_delete=models.PROTECT
    )
    wood = models.ForeignKey(
        Wood, verbose_name="نوع چوب", related_name="products", on_delete=models.PROTECT
    )
    price = models.PositiveBigIntegerField("قیمت (تومان)", validators=[MinValueValidator(0)])
    old_price = models.PositiveBigIntegerField("قیمت قبل از تخفیف", null=True, blank=True)
    badge = models.CharField("برچسب", max_length=30, blank=True)
    stock = models.PositiveIntegerField("موجودی", default=0)
    image = models.ImageField("تصویر", upload_to="products/", blank=True, null=True)
    image_url = models.CharField("آدرس تصویر", max_length=300, blank=True)
    alt = models.CharField("متن جایگزین تصویر", max_length=200, blank=True)
    is_active = models.BooleanField("فعال", default=True)
    order = models.PositiveSmallIntegerField("ترتیب", default=0)
    created_at = models.DateTimeField("تاریخ ثبت", auto_now_add=True)

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        ordering = ["order", "-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)[:120]
        super().save(*args, **kwargs)

    @property
    def in_stock(self) -> bool:
        return self.stock > 0

    def __str__(self):
        return self.title


class Order(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "جدید"
        CONFIRMED = "confirmed", "تأیید شده"
        SHIPPED = "shipped", "ارسال شده"
        CANCELED = "canceled", "لغو شده"

    full_name = models.CharField("نام و نام خانوادگی", max_length=120)
    phone = models.CharField("شماره تماس", max_length=20)
    address = models.TextField("آدرس", blank=True)
    note = models.TextField("توضیحات", blank=True)
    total = models.PositiveBigIntegerField("مبلغ کل", default=0)
    status = models.CharField("وضعیت", max_length=12, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField("تاریخ ثبت", auto_now_add=True)

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"
        ordering = ["-created_at"]

    def recalculate(self):
        self.total = sum(i.line_total for i in self.items.all())
        return self.total

    def __str__(self):
        return f"سفارش #{self.pk} — {self.full_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name="سفارش", related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name="محصول", on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField("تعداد", default=1, validators=[MinValueValidator(1)])
    unit_price = models.PositiveBigIntegerField("قیمت واحد", default=0)

    class Meta:
        verbose_name = "قلم سفارش"
        verbose_name_plural = "اقلام سفارش"

    @property
    def line_total(self) -> int:
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.product} × {self.quantity}"


class ConsultRequest(models.Model):
    full_name = models.CharField("نام و نام خانوادگی", max_length=120)
    phone = models.CharField("شماره تماس", max_length=20)
    message = models.TextField("شرح پروژه", blank=True)
    is_handled = models.BooleanField("پیگیری شد", default=False)
    created_at = models.DateTimeField("تاریخ ثبت", auto_now_add=True)

    class Meta:
        verbose_name = "درخواست مشاوره"
        verbose_name_plural = "درخواست‌های مشاوره"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} — {self.phone}"
