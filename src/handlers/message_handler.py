from typing import Any, Dict

from linebot.models import TextSendMessage

from ..domains.conversation_service import analyze_conversation_with_ollama


class LineBot:
    def __init__(self, line_bot_api: Any, reply_token: str):
        self.line_bot_api = line_bot_api
        self.reply_token = reply_token

    async def say(self, message: str) -> None:
        self.line_bot_api.reply_message(
            self.reply_token,
            TextSendMessage(text=message),
        )


async def process_message_event(event: Dict[str, Any], line_bot_api: Any) -> None:
    try:
        message = event["message"]
        text = message["text"]
        user_id = event["source"]["userId"]
        reply_token = event["replyToken"]

        line_bot = LineBot(line_bot_api, reply_token)

        if "groupId" in event["source"]:
            group_id = event["source"]["groupId"]

            try:
                profile = line_bot_api.get_group_member_profile(group_id, user_id)
                user_name = profile.display_name
                print(f"{user_name} > {text}")
            except Exception as e:
                print(f"ユーザー情報の取得に失敗: {e}")
                user_name = "Unknown User"

            response = await analyze_conversation_with_ollama(text)
            await line_bot.say(response)

        else:
            await line_bot.say(
                "このボットはグループ会話用です。グループに招待して使ってください。"
            )

    except Exception as e:
        await line_bot.say("申し訳ありません。処理中にエラーが発生しました。")
