from django.db.models.signals import Signal
from django.dispatch import receiver

from borrowing.models import Borrowing

borrowing_created = Signal()


@receiver(borrowing_created, sender=Borrowing)
def handle_borrowing_created(sender, instance, **kwargs):
    print(f"Borrowing created: {instance}")
