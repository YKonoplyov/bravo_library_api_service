from django.urls import path

from payment.views import (
    PaymentListView,
    PaymentDetailView,
    PaymentSessionCreateView,
    PaymentSuccessView,
    PaymentCancelView
)

urlpatterns = [
    path(
        "payments/",
        PaymentListView.as_view(),
        name="payment-list"
    ),
    path(
        "payments/<int:pk>/",
        PaymentDetailView.as_view(),
        name="payment-detail"
    ),
    path(
        "payments/create/",
        PaymentSessionCreateView.as_view(),
        name="session-create"
    ),
    path(
        "payments/success/",
        PaymentSuccessView.as_view(),
        name="payment-success"
    ),
    path(
        "payments/cancel/",
        PaymentCancelView.as_view(),
        name="payment-cancel"
    ),
]

app_name = "payment"
