from rest_framework.permissions import BasePermission

from services.notifications.bot_manager import TelegramBot


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.borrowing.user_id == request.user or request.user.is_staff


class TGBotActivated(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if user and user.chat_id is not None:
            return True

        bot = TelegramBot()
        chat_id = bot.get_chat_id_if_started(telegram_nick=user.telegram_nick[1:])

        if chat_id != -1:
            user.chat_id = chat_id
            user.save()
            return True

        return False
