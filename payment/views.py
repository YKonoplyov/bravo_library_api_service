from django.shortcuts import redirect
import stripe
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from borrowing.models import Borrowing
from library_config.settings import STRIPE_SECRET_KEY
from borrowing.permissions import IsOwnerOrAdmin
from payment.models import Payment
from payment.serializers import PaymentSerializer, PaymentDetailSerializer


OVERDUE_CONST = 2


class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        else:
            return Payment.objects.filter(borrowing__user_id=user)


class PaymentDetailView(generics.RetrieveAPIView):
    queryset = Payment.objects.all()
    permission_classes = [IsOwnerOrAdmin]
    serializer_class = PaymentDetailSerializer


stripe.api_key = STRIPE_SECRET_KEY


class PaymentSessionCreateView(generics.CreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        unpaid = Payment.objects.filter(
            borrowing__user_id=user.id
        ).filter(status="PENDING")
        if unpaid:
            return Response({"error": "you must end previous payment"})

        borrowing = Borrowing.objects.filter(user_id=user).last()

        if borrowing.actual_return_date is None:
            money_to_pay = self.calculate_money_to_pay(borrowing)
            payment_status = "PENDING"
            payment_type = "PAYMENT"
        else:
            money_to_pay = self.calculate_money_to_pay_fee(borrowing)
            payment_status = "PENDING"
            payment_type = "FINE"

        payment = Payment.objects.create(
            status=payment_status,
            type=payment_type,
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
            success_url="http://127.0.0.1:8000/api/payment/payments/success/",
            cancel_url="http://127.0.0.1:8000/api/payment/payments/cancel/",
        )

        payment.session_id = session.get("id")
        payment.session_url = session.get("url")
        payment.save()

        return redirect(session.get("url"), status=status.HTTP_302_FOUND)

    @staticmethod
    def calculate_money_to_pay(borrowing):
        days_in_usage = (
            borrowing.expected_return_date
            - borrowing.borrow_date
        ).days
        book_daily_fee = borrowing.book_id.daily_fee
        total_price = book_daily_fee * days_in_usage
        return total_price

    @staticmethod
    def calculate_money_to_pay_fee(borrowing):
        days_late = (
            borrowing.actual_return_date - borrowing.expected_return_date
        ).days
        book_daily_fee = borrowing.book_id.daily_fee
        total_price = (book_daily_fee * OVERDUE_CONST * days_late)
        return total_price


class PaymentSuccessView(APIView):

    def get(self, request):
        user_id = request.user.id
        payment = Payment.objects.filter(
            borrowing__user_id=user_id
        ).filter(status="PENDING").last()
        payment.status = "PAID"
        payment.save()

        return Response({"message": "payment success"})


class PaymentCancelView(APIView):
    def get(self, request):
        return Response(
            {"message": "payment cancelled, you can pay later"}
        )
