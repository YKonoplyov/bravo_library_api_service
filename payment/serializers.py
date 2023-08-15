from rest_framework import serializers

from borrowing.serializers import BorrowingSerializer
from payment.models import Payment


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = [
            "id",
            "status",
            "type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay"
        ]


class PaymentDetailSerializer(PaymentSerializer):
    borrowing = BorrowingSerializer(
        read_only=True,
        many=False
    )

    class Meta:
        model = Payment
        fields = [
            "status",
            "type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay"
        ]
