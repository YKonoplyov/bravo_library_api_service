from django.db.models.signals import Signal
from django.dispatch import receiver

from borrowing.models import Borrowing
from services.notifications.bot_manager import TelegramBot

borrowing_created = Signal()


@receiver(borrowing_created, sender=Borrowing)
def handle_borrowing_created(sender, instance, **kwargs):
    bot = TelegramBot()
    bot.send_borrowing_created_notification(instance)
