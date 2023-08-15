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
