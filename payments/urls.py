from django.urls import path, include

from payments.views import PaymentListView, PaymentDetailView

urlpatterns = [
    path("", PaymentListView.as_view(), name="payment-list"),
    path("<int:pk>/", PaymentDetailView.as_view(), name="payment-detail"),
]

app_name = "payments"
