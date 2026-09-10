from rest_framework import serializers

from reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            "id",
            "user",
            "user_name",
            "product",
            "rating",
            "title",
            "comment",
            "is_verified_purchase",
            "is_approved",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "user_name",
            "is_verified_purchase",
            "is_approved",
            "created_at",
            "updated_at",
        ]

    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.email
