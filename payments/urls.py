from django.urls import path

from payments.views import (
    PaymentListView,
    PaymentDetailView,
    PaymentSessionCreateView,
    PaymentSuccessView,
    PaymentCancelView
)

urlpatterns = [
    path("", PaymentListView.as_view(), name="payment-list"),
    path("<int:pk>/", PaymentDetailView.as_view(), name="payment-detail"),
    path("create/", PaymentSessionCreateView.as_view(), name="session-create"),
    path("success/", PaymentSuccessView.as_view(), name="payment-success"),
    path("cancel/", PaymentCancelView.as_view(), name="payment-cancel"),
]

app_name = "payments"
