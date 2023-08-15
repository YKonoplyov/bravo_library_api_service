from django.contrib.auth import get_user_model
from django.db import models

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

    @property
    def is_active(self):
        return not bool(self.actual_return_date)
