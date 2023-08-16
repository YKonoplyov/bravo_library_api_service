from django.core.management.base import BaseCommand
from borrowing.schedule_tasks import create_borrowing_check


class Command(BaseCommand):
    help = "Creates a borrowing check schedule"

    def handle(self, *args, **options):
        create_borrowing_check()

        self.stdout.write(self.style.SUCCESS(
            "Borrowing check schedule created"
        )
