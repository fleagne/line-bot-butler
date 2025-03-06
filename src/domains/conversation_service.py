from ollama import chat

from ..config import OLLAMA_MODEL


async def analyze_conversation_with_ollama(
    text: str,
) -> str:
    """
    Ollamaを使って会話履歴を分析する非同期関数
    """

    system_prompt = """
    あなたはLINEグループ会話を分析する専門AIです。与えられた会話履歴から以下の情報を抽出してください:
    1. 日程調整が必要かどうか(true/false)
    2. レストラン推薦が必要かどうか(true/false)
    3. 言及されている日付(YYYY-MM-DD形式、複数ある場合は最新のもの)
    4. 言及されている時間(HH:MM形式、複数ある場合は最新のもの)
    5. 言及されている場所・エリア名
    6. 食べ物の好みやジャンル(配列)
    7. 人数(数値)
    """

    try:
        response = chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
        )

        response_text = response.message.content
        print(response_text)

        return response_text if response_text else "情報が見つかりませんでした。"

    except Exception as e:
        return "エラーが発生しました。"
