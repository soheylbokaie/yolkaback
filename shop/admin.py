from django.contrib import admin
from django.utils.html import format_html

from .models import Category, ConsultRequest, Order, OrderItem, Product, Wood

admin.site.site_header = "پنل مدیریت یولکا وود"
admin.site.site_title = "یولکا وود"
admin.site.index_title = "مدیریت فروشگاه و سفارش‌ها"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "order"]
    list_editable = ["order"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Wood)
class WoodAdmin(admin.ModelAdmin):
    list_display = ["name_fa", "name_en", "texture"]
    search_fields = ["name_fa", "name_en"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["thumb", "title", "category", "wood", "price", "stock", "is_active", "order"]
    list_display_links = ["thumb", "title"]
    list_editable = ["price", "stock", "is_active", "order"]
    list_filter = ["category", "wood", "is_active"]
    search_fields = ["title", "description"]
    readonly_fields = ["created_at"]
    fieldsets = (
        ("مشخصات", {"fields": ("title", "slug", "description", "category", "wood")}),
        ("قیمت و موجودی", {"fields": ("price", "old_price", "stock", "badge", "is_active", "order")}),
        ("تصویر", {"fields": ("image", "image_url", "alt")}),
        ("سیستمی", {"fields": ("created_at",)}),
    )

    @admin.display(description="تصویر")
    def thumb(self, obj):
        src = obj.image.url if obj.image else obj.image_url
        if not src:
            return "—"
        return format_html('<img src="{}" style="height:44px;width:44px;object-fit:cover;border-radius:4px" />', src)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["line_total_display"]

    @admin.display(description="جمع ردیف")
    def line_total_display(self, obj):
        return f"{obj.line_total:,}"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "full_name", "phone", "total_display", "status", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["full_name", "phone"]
    inlines = [OrderItemInline]
    readonly_fields = ["total", "created_at"]
    actions = ["mark_confirmed", "mark_shipped"]

    @admin.display(description="مبلغ کل")
    def total_display(self, obj):
        return f"{obj.total:,} تومان"

    @admin.action(description="تأیید سفارش‌های انتخاب‌شده")
    def mark_confirmed(self, request, queryset):
        queryset.update(status=Order.Status.CONFIRMED)

    @admin.action(description="ارسال‌شده کردن سفارش‌ها")
    def mark_shipped(self, request, queryset):
        queryset.update(status=Order.Status.SHIPPED)


@admin.register(ConsultRequest)
class ConsultRequestAdmin(admin.ModelAdmin):
    list_display = ["full_name", "phone", "is_handled", "created_at"]
    list_filter = ["is_handled"]
    list_editable = ["is_handled"]
    search_fields = ["full_name", "phone", "message"]
