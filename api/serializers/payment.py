from rest_framework import serializers

from payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(
        source="order.order_number",
        read_only=True,
    )

    class Meta:
        model = Payment
        fields = [
            "id",
            "order",
            "order_number",
            "transaction_id",
            "authority",
            "method",
            "status",
            "amount",
            "gateway_response",
            "paid_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "transaction_id",
            "authority",
            "status",
            "gateway_response",
            "paid_at",
            "created_at",
            "updated_at",
        ]
