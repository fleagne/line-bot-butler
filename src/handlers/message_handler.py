from typing import Any, Dict

from sqlalchemy.orm import Session

from ..databases.models import Conversation
from ..utils.line_bot import LineBot


def process_message_event(
    event: Dict[str, Any], line_bot_api: Any, db: Session
) -> None:
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
                print(f"Error: failed to get member profile: {e}")
                user_name = "Unknown User"

            try:
                conversation = Conversation(
                    group_id=group_id,
                    user_id=user_id,
                    user_name=user_name,
                    message=text,
                )
                db.add(conversation)
                db.commit()
                db.refresh(conversation)
            except Exception as e:
                print(f"Error: failed to save conversation to db: {e}")

        else:
            line_bot.say(
                "このボットはグループ会話用です。グループに招待して使ってください。"
            )

    except Exception as e:
        print(f"Error: failed to handle message: {e}")
        line_bot.say("申し訳ありません。処理中にエラーが発生しました。")
