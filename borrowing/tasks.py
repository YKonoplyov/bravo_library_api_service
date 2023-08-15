from django.utils import timezone

from borrowing.models import Borrowing
from services.notification.bot_manager import TelegramBot


def get_overdue_borrowings():
    today_date = timezone.datetime.now().date()
    overdue_borrowings = Borrowing.objects.filter(
        actual_return_date__isnull=True, expected_return_date__lt=today_date
    ).select_related("user_id", "book_id")
    TelegramBot.send_notifications(overdue_borrowings)