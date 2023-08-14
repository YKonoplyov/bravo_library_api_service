from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from book.models import Book
from book.serializers import BookSerializer
from borrowing.models import Borrowing
from user.serializers import UserSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(BorrowingSerializer, self).validate(attrs=attrs)
        book_id = attrs.get("book_id").id
        book = Book.objects.get(id=book_id)
        if book.inventory == 0:
            raise ValidationError(f"There is no copies of {book.title}")
        return data

    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_return_date", "book_id")


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
        )
        read_only_fields = (
            "id",
            "borrow_date",
            "expected_return_date",
        )
