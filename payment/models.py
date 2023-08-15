<<<<<<< HEAD
from enum import Enum

from django.db import models

from borrowing.models import Borrowing


class StatusChoices(Enum):
    PENDING = "PENDING"
    PAID = "PAID"


class TypeChoices(Enum):
    PAYMENT = "PAYMENT"
    FINE = "FINE"


class Payment(models.Model):

    status = models.CharField(
        max_length=8,
        choices=[
            (_status.name, _status.value)
            for _status in StatusChoices
        ],
    )
    type = models.CharField(
        max_length=8,
        choices=[
            (_type.name, _type.value)
            for _type in TypeChoices
        ]
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
=======
from django.db import models

# Create your models here.
>>>>>>> 746f39a309cb78e07d3c21aaf5d97f0f0ef7fe5c
