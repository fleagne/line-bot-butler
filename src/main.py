import json

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError

from .config import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET
from .handlers.message_handler import process_message_event

app = FastAPI(title="Butler")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


@app.post("/callback")
async def webhook(request: Request):
    """
    LINE Webhookを処理するエンドポイント
    """
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
                    await process_message_event(event, line_bot_api)

        return JSONResponse(content={"status": "OK"})

    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


if __name__ == "__main__":
    print("Starting the FastAPI application...")
if __name__ == "__main__":
    print("Starting the FastAPI application...")
