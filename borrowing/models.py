from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from book.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)
    book_id = models.ForeignKey(
        Book,
        related_name="book",
        on_delete=models.CASCADE
    )
    user_id = models.ForeignKey(
        get_user_model(), related_name="user", on_delete=models.CASCADE
    )

    @staticmethod
    def validate_expected_return_date(expected_return):
        date_today = timezone.datetime.now().date()
        if expected_return < date_today:
            raise ValidationError("Expected return date can`t be in the past")

    @staticmethod
    def validate_book_inventory(book):
        if book.inventory == 0:
            raise ValidationError(f"There is no copies of {book.title}")

    def clean(self):
        Borrowing.validate_expected_return_date(
            self.borrow_date,
            self.expected_return_date
        )
        Borrowing.validate_book_inventory(
            self.book_id
        )
    @property
    def is_active(self):
        return not bool(self.actual_return_date)
