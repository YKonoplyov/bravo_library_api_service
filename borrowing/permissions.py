from rest_framework.permissions import BasePermission

from services import bot_manager


class TGBotActivated(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if user and user.chat_id is not None:
            return True

        chat_id = bot_manager.bot_get_chat_id_if_started(
            telegram_nick=user.telegram_nick[1:]
        )

        if chat_id != -1:
            user.chat_id = chat_id
            user.save()
            return True

        return False
