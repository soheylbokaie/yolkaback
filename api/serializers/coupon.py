from rest_framework import serializers

from coupons.models import Coupon


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = [
            "id",
            "code",
            "description",
            "percentage",
            "fixed_amount",
            "minimum_order_amount",
            "usage_limit",
            "used_count",
            "starts_at",
            "expires_at",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "used_count",
            "created_at",
            "updated_at",
        ]
