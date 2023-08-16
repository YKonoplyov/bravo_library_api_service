from django.db.models import Q
from django.utils import timezone

from borrowing.models import Borrowing
from services.notifications.bot_manager import TelegramBot

bot = TelegramBot()


def get_overdue_borrowings():
    today_date = timezone.datetime.now().date()
    active_borrowings = Borrowing.objects.filter(
        actual_return_date__isnull=True
    )
    overdue_borrowings = active_borrowings.filter(
        expected_return_date__lt=today_date
    )
    bot.send_notifications(overdue_borrowings_queryset=overdue_borrowings)
