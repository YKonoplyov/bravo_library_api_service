from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    telegram_nick = models.CharField(max_length=32, unique=True)
    chat_id = models.CharField(max_length=30, blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["telegram_nick"]

    objects = UserManager()

    @staticmethod
    def validate_telegram_nick(nick, raise_error):
        if len(nick) < 5 or len(nick) > 32:
            raise raise_error("Your nick must be in range (5, 32)")

        for char in nick:
            checks = [
                char.isdigit(),
                char.isalpha(),
                (char == "_"),
                (char == "@")
            ]
            if True not in checks:
                raise raise_error(
                    "Nick must contains only letters, digits and _"
                )

        if nick[0] == "@":
            if nick[1].isdigit() or nick[1] == "_":
                raise raise_error("First element must be letter")
        else:
            if nick[0].isdigit() or nick[0] == "_":
                raise raise_error("First element must be letter")

    def clean(self):
        User.validate_telegram_nick(self.telegram_nick, ValidationError)

    def save(
            self,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
    ):
        self.full_clean()
        self.validate_telegram_nick(self.telegram_nick, ValidationError)
        return super(User, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return f"{self.telegram_nick} - {self.email}"
