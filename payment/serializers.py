from rest_framework import serializers

from borrowing.serializers import BorrowingDetailSerializer
from payment.models import Payment


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = "__all__"


class PaymentDetailSerializer(PaymentSerializer):
    borrowing = BorrowingDetailSerializer(
        read_only=True,
        many=False
    )

    class Meta:
        fields = [
            "status",
            "type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay"
        ]
