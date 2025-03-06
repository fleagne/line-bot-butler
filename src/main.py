import json
import threading
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from sqlalchemy.orm import Session

from .config import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET
from .databases.db import get_db, init_db
from .databases.models import *  # noqa: F403 DBモデルをインポートしないと、初期構築でテーブルが作成されないため
from .handlers.message_handler import process_message_event
from .handlers.scheduler import Scheduler

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


@asynccontextmanager
async def lifespan(app: FastAPI):
    on_start()
    yield


app = FastAPI(title="Butler", lifespan=lifespan)


def start_scheduler(db: Session = Depends(get_db)):
    scheduler = Scheduler(line_bot_api, db)
    scheduler.start()


def on_start():
    init_db()

    db = next(get_db())
    scheduler_thread = threading.Thread(target=start_scheduler, args=(db,))
    scheduler_thread.daemon = True
    scheduler_thread.start()


@app.post("/callback")
async def webhook(request: Request, db: Session = Depends(get_db)):
    body = await request.body()
    body_str = body.decode("utf-8")
    signature = request.headers.get("X-Line-Signature", "")

    try:
        events = json.loads(body_str)["events"]

        handler.handle(body_str, signature)

        for event in events:
            event_type = event.get("type")

            if event_type == "message":
                if event["message"]["type"] == "text":
                    process_message_event(event, line_bot_api, db)

        return JSONResponse(content={"status": "OK"})

    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        print(f"Error: Webhook, {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


if __name__ == "__main__":
    print("Starting the FastAPI application...")
