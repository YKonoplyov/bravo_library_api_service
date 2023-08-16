from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase


class UserTest(TestCase):

    def test_correct_telegram_nick_validation(self):
        user = get_user_model().objects.create_user(
            email="test@example.com",
            password="password",
            telegram_nick="user_123"
        )
        self.assertIsNotNone(user)

    def test_incorrect_telegram_nick_validation(self):
        with self.assertRaisesMessage(ValidationError, "Your nick must be in range (5, 32)"):
            get_user_model().objects.create_user(
                email="test@example.com",
                password="password",
                telegram_nick='nick'
            )

        with self.assertRaisesMessage(ValidationError, "Nick must contains only letters, digits and _"):
            get_user_model().objects.create_user(
                email="test@example.com",
                password="password",
                telegram_nick="user_123!"
            )

        with self.assertRaisesMessage(ValidationError, "First element must be letter"):
            get_user_model().objects.create_user(
                email="test@example.com",
                password="password",
                telegram_nick="_ser_123"
            )

    def test_telegram_nick_signal(self):
        user = get_user_model().objects.create_user(
            email="test@example.com",
            password="password",
            telegram_nick="user_123"
        )

        user2 = get_user_model().objects.create_user(
            email="test2@example.com",
            password="password",
            telegram_nick="user2_123"
        )

        self.assertEqual(user.telegram_nick, "@user_123")
        self.assertEqual(user2.telegram_nick, "@user2_123")

    def test_user_create(self):
        user = get_user_model().objects.create_user(
            email="test@example.com",
            password="password",
            telegram_nick="user_123"
        )

        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.telegram_nick, "@user_123")
        self.assertTrue(user.check_password("password"))
