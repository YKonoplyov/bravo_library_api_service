from rest_framework import serializers

from book.serializers import BookSerializer
from borrowing.models import Borrowing
from user.serializers import UserSerializer


class BorrowingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = "__all__"
        extra_kwargs = {"actual_return_date": {"write_only": True}}


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = "__all__"
        read_only_fields = (
            "id",
            "borrow_date",
            "borrowing_date"
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )