from enum import Enum

from django.db import models


class CoverType(Enum):
    HARD = "Hard cover"
    SOFT = "Soft cover"


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(
        max_length=10,
        choices=[
            (cover_type.name, cover_type.value)
            for cover_type in CoverType
        ]
    )
    inventory = models.PositiveIntegerField(default=0)
    daily_fee = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return (
            f"{self.title} (author: {self.author},"
            f" daily fee: {self.daily_fee})"
        )
