from django.utils import timezone

from borrowing.models import Borrowing
from services.notification.bot_manager import TelegramBot


def get_overdue_borrowings():
    today_date = timezone.datetime.now().date()
    overdue_borrowings = Borrowing.objects.filter(
        actual_return_date__lt=today_date
    )
    TelegramBot.send_message(overdue_borrowings)
    """uncomment to activate message sending 
    for users fir overdued borrowings"""