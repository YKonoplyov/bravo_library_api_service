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
            success_url="http://127.0.0.1:8000/api/payment/payments/success/",
            cancel_url="http://127.0.0.1:8000/api/payment/payments/cancel/",
        )

        payment.session_id = session.get("id")
        payment.session_url = session.get("url")
        payment.save()

        return Response(data=session, status=status.HTTP_201_CREATED)


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
