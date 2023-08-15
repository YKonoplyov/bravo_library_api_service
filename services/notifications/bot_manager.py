import requests

TOKEN = "6200280006:AAEohwzJIDKMwGElXWMFlFmQGRtAMxmk808"
TG_API_URL = "https://api.telegram.org/bot"


class TelegramBot:
    base_url = TG_API_URL + TOKEN

    def send_message(self, message_text: str, chat_id: str) -> None:
        """Send message to given chat id with given message text"""
        url = f"{self.base_url}/sendMessage?chat_id={chat_id}&text={message_text}"
        requests.get(url=url)

    def send_notifications(self, receivers: list):
        pass

    def get_chat_id_if_started(self, telegram_nick: str) -> str | int:
        """telegram API checking if there is user /start command with given username"""
        url = f"{self.base_url}/getUpdates"
        response = requests.get(url=url).json()
        messages = response["result"]

        for message_object in messages[::-1]:
            message = message_object.get("message")
            if message is not None:
                if (
                    message["from"]["username"] == telegram_nick
                    and message["text"] == "/start"
                ):
                    chat_id = message["chat"]["id"]
                    self.send_message(
                        message_text="Successfully registered, you can borrow books now",
                        chat_id=chat_id,
                    )
                    return chat_id

        return -1

    def send_borrowing_created_notification(self, instance):
        last_borrowing = instance.last()
        active_borrowings = [
            borrow for borrow in instance.all() if borrow.is_active == 1
        ]

        chat_id = last_borrowing.user_id.chat_id
        message = (
            f"You created new borrowing!\n"
            f"-------------------------\n"
            f"Title: {last_borrowing.book_id.title}\n"
            f"Author: {last_borrowing.book_id.author}\n"
            f"Cover: {last_borrowing.book_id.cover}\n"
            f"Return to {last_borrowing.expected_return_date}\n"
            f"-------------------------\n"
            f"Your active borrowings\n"
        )

        for active_borrowing in active_borrowings:
            message += (
                f"- Book title: {active_borrowing.book_id.title},"
                f" expected return date "
                f"{active_borrowing.expected_return_date}\n"
            )

        self.send_message(
            message_text=message,
            chat_id=chat_id,
        )
