from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Address


class AddressInline(admin.TabularInline):
    model = Address

    extra = 0

    fields = (
        "title",
        "address_type",
        "recipient_name",
        "recipient_phone",
        "province",
        "city",
        "postal_code",
        "is_default",
    )


@admin.register(User)
class UserAdmin(BaseUserAdmin):

    list_display = (
        "email",
        "first_name",
        "last_name",
        "phone_number",
        "role",
        "is_active",
        "is_email_verified",
        "created_at",
        "last_login",
    )

    list_filter = (
        "role",
        "is_active",
        "is_superuser",
        "is_email_verified",
        "is_phone_verified",
        "gender",
        "created_at",
    )

    search_fields = (
        "email",
        "first_name",
        "last_name",
        "phone_number",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "last_login",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Authentication",
            {
                "fields": (
                    "email",
                    "password",
                )
            },
        ),
        (
            "Personal Information",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone_number",
                    "date_of_birth",
                    "gender",
                )
            },
        ),
        (
            "Account",
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_superuser",
                )
            },
        ),
        (
            "Verification",
            {
                "fields": (
                    "is_email_verified",
                    "is_phone_verified",
                )
            },
        ),
        (
            "Marketing",
            {
                "fields": (
                    "marketing_emails",
                    "marketing_sms",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Dates",
            {
                "fields": (
                    "last_login",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            "Account",
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                ),
            },
        ),
        (
            "Personal Information",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone_number",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_superuser",
                )
            },
        ),
    )

    inlines = (AddressInline,)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "user",
        "recipient_name",
        "recipient_phone",
        "province",
        "city",
        "postal_code",
        "is_default",
        "created_at",
    )

    list_filter = (
        "address_type",
        "is_default",
        "province",
        "city",
        "created_at",
    )

    search_fields = (
        "title",
        "user__email",
        "user__first_name",
        "user__last_name",
        "recipient_name",
        "recipient_phone",
        "postal_code",
        "address",
    )

    autocomplete_fields = ("user",)

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "-is_default",
        "-created_at",
    )
