from django.core.management.base import BaseCommand



class Command(BaseCommand):
    help = "Creates a borrowing check schedule"

    def handle(self, *args, **options):
        from borrowing import schedule_tasks
        schedule_tasks

        self.stdout.write(
            self.style.SUCCESS(
                "Borrowing check schedule created"
            )
        )
