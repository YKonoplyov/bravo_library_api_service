from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from book.models import Book
from book.serializers import BookSerializer
from borrowing.models import Borrowing
from user.serializers import UserSerializer


class BorrowingSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        data = super(BorrowingSerializer, self).validate(attrs=attrs)
        Borrowing.validate_expected_return_date(
            attrs["expected_return_date"]
        )
        Borrowing.validate_book_inventory(
            attrs.get("book_id")
        )
        print(attrs)
        return data

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "book_id",
            "actual_return_date",
            "is_active"
        )
        read_only_fields = ("id", "actual_return_date")


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookSerializer(read_only=True, many=False, source="book_id")
    user = UserSerializer(read_only=True, many=False, source="user_id")

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "book",
            "user",
            "is_active",
        )
        read_only_fields = (
            "id",
            "borrow_date",
            "expected_return_date",
        )


class BorrowingReturnSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "book_id",
            "actual_return_date",
        )
        read_only_fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "book_id",
            "actual_return_date",
        )
