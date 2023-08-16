from django.utils import timezone
from django_q.models import Schedule


def create_borrowing_check():
    Schedule.objects.create(
        func="borrowing.tasks.get_overdue_borrowings",
        schedule_type=Schedule.DAILY,
        repeats=-1,
        next_run=timezone.datetime.now().replace(hour=12, minute=0)
    )


create_borrowing_check()
