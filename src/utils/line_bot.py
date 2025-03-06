from typing import Any

from linebot.models import TextSendMessage


class LineBot:
    def __init__(self, line_bot_api: Any, reply_token: str | None = None):
        self.line_bot_api = line_bot_api
        self.reply_token = reply_token

    def say(self, message: str) -> None:
        if self.reply_token:
            self.line_bot_api.reply_message(
                self.reply_token,
                TextSendMessage(text=message),
            )

    def push_message(self, to: str, message: str) -> None:
        self.line_bot_api.push_message(
            to,
            TextSendMessage(text=message),
        )
