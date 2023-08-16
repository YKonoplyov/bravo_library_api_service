from django.db.models import Q
from django.utils import timezone

from borrowing.models import Borrowing
from services.notification.bot_manager import TelegramBot


def get_overdue_borrowings():
    today_date = timezone.datetime.now().date()
    active_borrowings = Borrowing.objects.filter(
        actual_return_date__isnull=True
    )
    overdue_borrowings = active_borrowings.filter(
        expected_return_date__lt=today_date
    )
    TelegramBot.send_notification(overdue_borrowings)
