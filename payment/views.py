<<<<<<< HEAD
import stripe
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from borrowing.models import Borrowing
from library_config.settings import STRIPE_SECRET_KEY
from borrowing.permissions import IsOwnerOrAdmin
from payment.models import Payment
from payment.serializers import PaymentSerializer


class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        else:
            return Payment.objects.filter(user=user)


class PaymentDetailView(generics.RetrieveAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsOwnerOrAdmin]


stripe.api_key = STRIPE_SECRET_KEY


class PaymentSessionCreateView(generics.CreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        payment_serializer = self.get_serializer(data=request.data)
        payment_serializer.is_valid(raise_exception=True)

        borrowing = Borrowing.objects.get(id=request.data.get("borrowing"))
        money_to_pay = request.data.get("money_to_pay")

        payment = Payment.objects.create(
            status=request.data.get("status"),
            type=request.data.get("type"),
            money_to_pay=money_to_pay,
            borrowing=borrowing
        )

        # Create a Stripe Payment Session
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "unit_amount": int(float(money_to_pay) * 100),
                    "product_data": {
                        "name": "Book Borrowing",
                    },
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url="http://127.0.0.1:8000/api/payments/success/",
            cancel_url="http://127.0.0.1:8000/api/payments/cancel/",
        )

        payment.session_id = session.get("id")
        payment.session_url = session.get("url")
        payment.save()

        return Response(data=session, status=status.HTTP_201_CREATED)


class PaymentSuccessView(APIView):

    def get(self, request):
        user_id = request.user.id
        payment = Payment.objects.filter(borrowing__user_id=user_id).last()
        payment.status = Payment.StatusChoices.PAID
        payment.save()

        return Response({"message": "payment success"})


class PaymentCancelView(APIView):

    def get(self, request):
        return Response({"message": "payment cancelled"})
=======
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView

from borrowing.models import Borrowing

OVERDUE_CONST = 2


class PaymentView(APIView):
    def get(self, request, borrowing_id):
        borrowing = get_object_or_404(Borrowing, id=borrowing_id)
        return HttpResponse(
            {"money_to_pay": self.calculate_money_to_pay(borrowing)}
        )

    @staticmethod
    def calculate_money_to_pay(borrowing):
        if not borrowing.actual_return_date:
            return 0

        if borrowing.actual_return_date <= borrowing.expected_return_date:
            actual_return_date = (
                borrowing.expected_return_date - borrowing.actual_return_date
            ).days
            days_in_usage = borrowing.actual_return_date - actual_return_date
            book_daily_fee = borrowing.book_id.daily_fee
            total_price = book_daily_fee * days_in_usage
            return total_price

        days_late = (
            borrowing.actual_return_date - borrowing.expected_return_date
        ).days
        book_daily_fee = borrowing.book_id.daily_fee
        total_price = (book_daily_fee * OVERDUE_CONST * days_late) + (
            borrowing.expected_return_date - borrowing.borrow_date
        ) * book_daily_fee
        return total_price
>>>>>>> 746f39a309cb78e07d3c21aaf5d97f0f0ef7fe5c
