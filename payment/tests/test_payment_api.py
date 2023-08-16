import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from book.models import Book
from borrowing.models import Borrowing
from payment.models import Payment
from payment.serializers import PaymentSerializer, PaymentDetailSerializer
from user.models import User

PAYMENTS_URL = reverse("payment:payment-list")
PAYMENTS_CREATE_URL = reverse("payment:session-create")
PAYMENT_SUCCESS_URL = reverse("payment:payment-success")
PAYMENT_CANCEL_URL = reverse("payment:payment-cancel")


def sample_book() -> Book:
    return Book.objects.create(
        title="Book1",
        author="Author",
        cover="HARD",
        inventory=5,
        daily_fee=2.00
    )


def sample_borrowing(book: Book, user: User) -> Borrowing:
    return Borrowing.objects.create(
        borrow_date=datetime.date.today(),
        expected_return_date=datetime.date.today() + datetime.timedelta(days=3),
        actual_return_date=None,
        book_id=book,
        user_id=user
    )


class UnauthenticatedPaymentApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_authenticate_required(self):
        response = self.client.get(PAYMENTS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPaymentApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user1 = get_user_model().objects.create_user(
            email="user1@user.com",
            telegram_nick="@user12",
            password="pwd12345",
            chat_id=1
        )
        self.user2 = get_user_model().objects.create_user(
            email="user2@user.com",
            telegram_nick="@user122",
            password="pwd12345",
            chat_id=2
        )
        self.client.force_authenticate(self.user1)

    def test_payment_create(self):
        book = sample_book()
        borrowing = sample_borrowing(book, self.user1)
        payload = {
            "status": "PENDING",
            "type": "PAYMENT",
            "borrowing": borrowing,
            "money_to_pay": 6.00
        }
        response = self.client.post(PAYMENTS_CREATE_URL, payload)
        payment = Payment.objects.last()
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(payment.borrowing.pk, borrowing.pk)

    def test_user_can_list_only_own_payments(self):
        book = sample_book()
        borrowing1 = sample_borrowing(book, self.user1)
        borrowing2 = sample_borrowing(book, self.user2)

        payment1 = Payment.objects.create(
            status="PENDING",
            type="PAYMENT",
            borrowing=borrowing1,
            money_to_pay=6.00
        )
        payment2 = Payment.objects.create(
            status="PENDING",
            type="PAYMENT",
            borrowing=borrowing2,
            money_to_pay=6.00
        )

        response = self.client.get(PAYMENTS_URL)

        serializer1 = PaymentSerializer(payment1)
        serializer2 = PaymentSerializer(payment2)

        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)

    def test_user_cant_retrieve_not_own_payment(self):
        book = sample_book()
        borrowing = sample_borrowing(book, self.user2)

        payment = Payment.objects.create(
            status="PENDING",
            type="PAYMENT",
            borrowing=borrowing,
            money_to_pay=6.00
        )

        response = self.client.get(PAYMENTS_URL + f"{payment.pk}/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_retrieve_own_payment(self):
        book = sample_book()
        borrowing = sample_borrowing(book, self.user1)

        payment = Payment.objects.create(
            status="PENDING",
            type="PAYMENT",
            borrowing=borrowing,
            money_to_pay=6.00
        )

        response = self.client.get(PAYMENTS_URL + f"{payment.pk}/")

        serializer = PaymentDetailSerializer(payment)

        self.assertEqual(serializer.data, response.data)


class AdminPaymentsApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user1 = get_user_model().objects.create_user(
            email="user1@user.com",
            telegram_nick="@user12",
            password="pwd12345",
            chat_id=1
        )
        self.user2 = get_user_model().objects.create_user(
            email="user2@user.com",
            telegram_nick="@user122",
            password="pwd12345",
            chat_id=2
        )
        self.admin = get_user_model().objects.create_user(
            email="admin@admin.com",
            telegram_nick="@admin1",
            password="pwd12345",
            chat_id=3,
            is_staff=True
        )
        self.client.force_authenticate(self.admin)

    def test_admin_can_list_all_payments(self):
        book = sample_book()
        borrowing1 = sample_borrowing(book, self.user1)
        borrowing2 = sample_borrowing(book, self.user2)

        payment1 = Payment.objects.create(
            status="PENDING",
            type="PAYMENT",
            borrowing=borrowing1,
            money_to_pay=6.00
        )
        payment2 = Payment.objects.create(
            status="PENDING",
            type="PAYMENT",
            borrowing=borrowing2,
            money_to_pay=6.00
        )

        response = self.client.get(PAYMENTS_URL)

        serializer1 = PaymentSerializer(payment1)
        serializer2 = PaymentSerializer(payment2)

        self.assertIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)

    def test_admin_can_retrieve_any_payment(self):
        book = sample_book()
        borrowing = sample_borrowing(book, self.user1)

        payment = Payment.objects.create(
            status="PENDING",
            type="PAYMENT",
            borrowing=borrowing,
            money_to_pay=6.00
        )

        response = self.client.get(PAYMENTS_URL + f"{payment.pk}/")

        serializer = PaymentDetailSerializer(payment)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data)


class PaymentSystemSuccessCancelUrlsTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@user.com",
            telegram_nick="@user12",
            password="pwd12345",
            chat_id=1
        )
        self.client.force_authenticate(self.user)

    def test_success_payment_return_success_message(self):
        book = sample_book()
        borrowing = sample_borrowing(book, self.user)

        payment = Payment.objects.create(
            status="PENDING",
            type="PAYMENT",
            borrowing=borrowing,
            money_to_pay=6.00
        )

        response = self.client.get(PAYMENT_SUCCESS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "payment success"})

    def test_cancelled_payment_return_cancel_message(self):

        response = self.client.get(PAYMENT_CANCEL_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {"message": "payment cancelled, you can pay later"}
        )
