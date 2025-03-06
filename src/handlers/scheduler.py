import time
from datetime import datetime
from typing import Any

import schedule
from ollama import chat
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import GROUP_ID, OLLAMA_MODEL
from ..databases.models import Conversation, Meeting
from ..utils.line_bot import LineBot


class MeetingModel(BaseModel):
    title: str
    date: str
    location: str
    status: str
    last_activity: str
    summary: str
    needs_date: bool
    needs_location: bool
    needs_reservation: bool
    reminder_sent: bool


class Scheduler:
    def __init__(self, line_bot_api: Any, db: Session):
        self.line_bot_api = line_bot_api
        self.line_bot = LineBot(self.line_bot_api)
        self.db = db

    def check_meetings(self):
        print("Checking meetings...")

        # 会話の取得
        try:
            conversations = self.db.scalars(
                select(Conversation).where(Conversation.group_id == GROUP_ID)
            ).all()

            conv_dict = [
                {c.name: getattr(conv, c.name) for c in conv.__table__.columns}
                for conv in conversations
            ]

            print(conv_dict)

        except Exception as e:
            print(f"Error: failed to fetch conversations: {e}")

        # 要約の作成
        try:
            system_prompt = """
            あなたは会話情報に基づき、会話の要約を支援するAIアシスタントです。
            次の情報に基づいて、会話の要約を作成してください。
            要約したメッセージだけを回答してください。
            
            以下のポイントを意識してください：
            1. 遊ぶ日程が決まっているかどうか
            """

            response = chat(
                model=OLLAMA_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": "\n".join(
                            [
                                f"{conv['user_name']} > {conv['message']}"
                                for conv in conv_dict
                            ]
                        ),
                    },
                ],
                stream=False,
            )

            summary = response.message.content
            print(summary)

        except Exception as e:
            print(f"Error: failed to create summary: {e}")

        try:
            system_prompt = """
            Based on the summary information, output the following information
            needs_date is bool and should return True if you need my intervention to arrange the dates, False if you do not.

            example:
            3月末に遊ぶことを検討している。具体的な日程は未定。
            needs_date: True

            4月1日に遊ぶことを決定した。
            needs_date: False
            """

            response = chat(
                model="llama3.2:latest",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": summary,
                    },
                ],
                format=MeetingModel.model_json_schema(),
                stream=False,
            )

            judge = MeetingModel.model_validate_json(response.message.content)
            print(judge)

        except Exception as e:
            print(f"Error: failed to create output: {e}")

        try:
            meeting = Meeting(
                group_id=GROUP_ID,
                title=judge.title,
                date=datetime.now(),
                location=judge.location,
                status=judge.status,
                last_activity=datetime.now(),
                summary=summary,
                needs_date=judge.needs_date,
                needs_location=judge.needs_location,
                needs_reservation=judge.needs_reservation,
                reminder_sent=judge.reminder_sent,
            )
            self.db.add(meeting)
            self.db.commit()
            self.db.refresh(meeting)

        except Exception as e:
            print(f"Error: failed to save summary to db: {e}")

        if judge.needs_date:
            try:
                system_prompt = """
                あなたはLINEグループの会話を支援するAIアシスタントです。
                分析結果に基づいて、自然で親しみやすい介入メッセージを作成してください。
                完成したメッセージだけを回答してください。

                以下のポイントを意識してください：
                1. フレンドリーで自然な口調を使用
                2. 分析結果の確信度に応じて表現を調整
                3. 具体的な日時を決めるための提案を行う
                4. 押し付けがましくならないよう配慮
                5. 定型文は避け、状況に応じた柔軟な表現を使用
                """

                response = chat(
                    model=OLLAMA_MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt,
                        },
                        {"role": "user", "content": summary},
                    ],
                    stream=False,
                )

                content = response["message"]["content"]
                print(content)
                self.line_bot.push_message(GROUP_ID, content)

            except Exception as e:
                print(f"Error: failed to create a content: {e}")

    def start(self):
        print("Scheduler started.")
        schedule.every(1).hours.do(self.check_meetings)

        # 一度jobを実行した時点でモジュールが終了してしまうため、while文で無限ループ状態にする必要がある
        while True:
            schedule.run_pending()
            time.sleep(1)
