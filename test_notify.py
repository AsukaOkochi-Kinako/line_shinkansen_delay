"""
LINE通知のテストスクリプト
--------------------------
実際の遅延がなくても、テスト通知をLINEに送信して動作確認できます。
使い方: python test_notify.py
"""

import os
import requests

LINE_API_URL = "https://api.line.me/v2/bot/message/push"


def send_line_message(text: str) -> None:
    token   = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
    user_id = os.environ["LINE_USER_ID"]

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "to": user_id,
        "messages": [{"type": "text", "text": text}],
    }
    resp = requests.post(LINE_API_URL, headers=headers, json=payload, timeout=15)

    if resp.status_code == 200:
        print("✅ LINE送信成功！LINEを確認してください。")
    else:
        print(f"❌ 送信失敗: {resp.status_code}")
        print(resp.text)


if __name__ == "__main__":
    message = (
        "🧪 これはテスト通知です\n\n"
        "🚨 東海道新幹線 遅延・運行障害情報\n"
        "確認時刻: 2026/05/13 12:00\n\n"
        "区間: 東京〜名古屋\n"
        "状況: 遅延\n"
        "原因: 地震\n"
        "　発生時刻　11:45\n\n"
        "詳細: https://traininfo.jr-central.co.jp/shinkansen/sp/ja/index.html"
    )
    send_line_message(message)
