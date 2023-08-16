from django.core.management.base import BaseCommand
import schedule_tasks


class Command(BaseCommand):
    help = "Creates a borrowing check schedule"

    def handle(self, *args, **options):
        schedule_tasks

        self.stdout.write(self.style.SUCCESS(
            "Borrowing check schedule created"
        )
