from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from book.models import Book
from borrowing.models import Borrowing


def sample_book(**params):
    defaults = {
        "title": "Sample book",
        "author": "Sample author",
        "cover": "SOFT",
        "inventory": 90,
        "daily_fee": 15,
    }
    defaults.update(params)
    return Book.objects.create(**defaults)


def sample_user(**params):
    defaults = {
        "email": "rand@email.com",
        "telegram_nick": "@stripelover228",
        "password": "testpass321",
    }
    defaults.update(params)
    return get_user_model().objects.create(**defaults)


def sample_borrowing(**params):
    time_now = timezone.now().date()

    defaults = {
        "borrow_date": time_now,
        "expected_return_date":  time_now + timezone.timedelta(days=5),
        "actual_return_date": None,
        "book_id": sample_book(),
        "user_id": None,
    }
    defaults.update(params)
    return Borrowing.objects.create(**defaults)


class TestBorrowingModel(TestCase):
    def setUp(self):
        self.user = sample_user()
        self.time_now = timezone.now().date()
        self.borrowing_1 = sample_borrowing(user_id=self.user)
        self.borrowing_2 = sample_borrowing(
            user_id=self.user,
            actual_return_date=timezone.now().date()
        )

    def test_is_active(self):
        self.assertEqual(self.borrowing_1.is_active, True)
        self.assertEqual(self.borrowing_2.is_active, False)

    def test_validate_expected_return_date(self):
        with self.assertRaises(ValidationError):
            Borrowing.objects.create(
                expected_return_date=(self.time_now - timezone.timedelta(days=5)),
                actual_return_date=None,
                book_id=sample_book(),
                user_id=self.user,
            )

    def test_validate_book_inventory(self):
        book = sample_book(inventory=0)
        with self.assertRaises(ValidationError):
            sample_borrowing(book_id=book, user_id=self.user)


    def test_str_method(self):
        borrowing = sample_borrowing(
                    expected_return_date=(self.time_now - timedelta(days=2)),
                    user_id=self.user
                )
        test_string = ("Sample book was borrowed from "
                       "2023-08-16 to expected 2023-08-14")
        self.assertEqual(borrowing.__str__(), test_string)
