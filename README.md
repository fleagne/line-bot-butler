# LINE Bot Butler

グループ会話を分析して、遊びの日程調整や要約をサポートしてくれるLINE Bot

## 起動方法

```bash
uv run uvicorn src.main:app --reload
```

## ngrokで公開する場合

```bash
sudo ngrok http 8000
```

Messaging APIのWebhook URLに、ngrokのURLを設定する

```txt
https://44fb-124-87-105-233.ngrok-free.app/callback
```

## 機能

- 遊ぶ日程が決まらなそうだったら、遊ぶ日程を決めるよう促す
- 遊び先が決まらなそうだったら、遊ぶ先を探すよう促す
- 遊び先が決まったら、予約をするかお伺いを立てる
- 遊ぶ日程に近づいてきたら、予定のリマインドをする
- 会話が停滞していたら促す
- 雑談には加わらない（予定関連の話題のみ反応）
