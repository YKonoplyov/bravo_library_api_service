from django.db import models

from borrowing.models import Borrowing


class Payment(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "Pending"
        PAID = "Paid"

    class TypeChoices(models.TextChoices):
        PAYMENT = "Payment"
        FINE = "Fine"

    status = models.CharField(
        max_length=8,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING
    )
    type = models.CharField(
        max_length=8,
        choices=TypeChoices.choices,
        default=TypeChoices.PAYMENT
    )
    borrowing = models.ForeignKey(
        Borrowing,
        on_delete=models.CASCADE
    )
    session_url = models.URLField(blank=True)
    session_id = models.CharField(max_length=255, blank=True)
    money_to_pay = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.status} {self.session_id} {self.money_to_pay}"
