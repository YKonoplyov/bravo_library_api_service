from django.apps import AppConfig


class BorrowingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "borrowing"
<<<<<<< HEAD

    def ready(self):
        import borrowing.signals
=======
>>>>>>> 746f39a309cb78e07d3c21aaf5d97f0f0ef7fe5c
