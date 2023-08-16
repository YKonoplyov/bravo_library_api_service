from django.utils import timezone
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from borrowing.models import Borrowing
from book.models import Book
from borrowing.serializers import BorrowingSerializer, BorrowingDetailSerializer
from borrowing.signals import handle_borrowing_created

BORROWING_URL = reverse("borrowing:borrowing-list")


def sample_book(**params):
    defaults = {
        "title": "Test book",
        "author": "test author",
        "cover": "Hard cover",
        "inventory": 2,
        "daily_fee": 2
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


def sample_user(**params):
    defaults = {
        "email": "test1@example.com",
        "password": "password",
        "telegram_nick": "user1_123"
    }
    defaults.update(params)

    return get_user_model().objects.create(**defaults)


def sample_borrowing(user, **params):
    now = timezone.now().date()
    defaults = {
        "expected_return_date": now + timezone.timedelta(days=5),
        "book_id": sample_book(),
        "user_id": user,
    }
    defaults.update(params)

    with patch("payment.views.PaymentSessionCreateView") as MockPaymentService:
        mock_payment_service_instance = MockPaymentService.return_value
        mock_payment_service_instance.make_payment.return_value = True

        return Borrowing.objects.create(**defaults)


def detail_url(borrowing_id):
    return reverse("borrowing:borrowing-detail", args=[borrowing_id])


def return_book_url(borrowing_id):
    return reverse("borrowing:borrowing-return-book", args=[borrowing_id])


class UnauthorizedBorrowingTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(BORROWING_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_no_chat_id(self):
        user = sample_user()
        self.client.force_authenticate(user)

        response = self.client.get(BORROWING_URL)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AuthorizedBorrowingTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

        self.user = sample_user(
            email="testmain@example.com",
            telegram_nick="main_user1"
        )
        self.user.chat_id = "fghjk"

        self.client.force_authenticate(self.user)

    def test_users_borrowings_list(self):
        sample_borrowing(user=self.user)

        response = self.client.get(BORROWING_URL)
        borrowings = Borrowing.objects.all()

        serializer = BorrowingSerializer(borrowings, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_no_users_borrowings_list(self):
        sample_borrowing(user=sample_user())

        response = self.client.get(BORROWING_URL)
        borrowings = Borrowing.objects.all()

        serializer = BorrowingSerializer(borrowings, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data, serializer.data)

    def test_filter_borrowings_by_is_active(self):
        borrowing1 = sample_borrowing(user=self.user)
        borrowing2 = sample_borrowing(user=self.user)
        borrowing2.actual_return_date = borrowing2.expected_return_date
        borrowing2.save()

        response = self.client.get(
            BORROWING_URL, {"is_active": "1"}
        )

        serializer1 = BorrowingSerializer(borrowing1)
        serializer2 = BorrowingSerializer(borrowing2)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)

    def test_borrowings_detail(self):
        borrowing = sample_borrowing(user=self.user)

        response = self.client.get(detail_url(borrowing.id))
        serializer = BorrowingDetailSerializer(borrowing)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data)

    def test_borrowing_create(self):
        book = sample_book()
        now = timezone.now().date()
        data = {
            "expected_return_date": now + timezone.timedelta(days=5),
            "book_id": book.id,
            "user_id": self.user,
        }

        response = self.client.post(BORROWING_URL, data)

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        book.refresh_from_db()

        self.assertEqual(book.inventory, 1)
        self.assertTrue(handle_borrowing_created)

    def test_borrowing_return(self):
        borrowing = sample_borrowing(user=self.user)
        book = Book.objects.get(id=borrowing.book_id.id)
        inventory = book.inventory

        response = self.client.get(return_book_url(borrowing_id=borrowing.id))
        borrowing.refresh_from_db()
        book.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(borrowing.actual_return_date, timezone.datetime.now().date())
        self.assertEqual(book.inventory, inventory + 1)


class AdminBorrowingTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create(
            email="test@example.com",
            password="password",
            telegram_nick="user_123",
            is_staff=True
        )
        self.user.chat_id = "fghjk"
        self.user.save()

        self.client.force_authenticate(self.user)

    def test_filter_borrowing_by_user_id(self):
        borrowing1 = sample_borrowing(user=self.user)
        borrowing2 = sample_borrowing(user=sample_user())

        response = self.client.get(
            BORROWING_URL, {"users": f"{self.user.id}"}
        )

        serializer1 = BorrowingSerializer(borrowing1)
        serializer2 = BorrowingSerializer(borrowing2)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)

