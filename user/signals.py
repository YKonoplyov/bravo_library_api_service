from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=get_user_model())
def add_at_symbol_to_telegram_nick(sender, instance, created, **kwargs):
    if created and not instance.telegram_nick.startswith("@"):
        instance.telegram_nick = "@" + instance.telegram_nick
        instance.save()
