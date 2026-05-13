"""
東海道新幹線 遅延監視スクリプト
-------------------------------
JR東海の運行情報APIを定期的に確認し、遅延・運転見合わせが発生した場合に
LINE Messaging API でプッシュ通知を送信します。

必要な環境変数:
  LINE_CHANNEL_ACCESS_TOKEN : LINE チャネルアクセストークン
  LINE_USER_ID              : 通知先のユーザーID (Uxxxxxxxx...)
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta

import requests

# ─── 定数 ────────────────────────────────────────────────
JST = timezone(timedelta(hours=9))

# JR東海 運行情報 JSON エンドポイント
JR_MAIN_URL = "https://traininfo.jr-central.co.jp/shinkansen/sp/ja/index.html"
JR_API_URL  = "https://traininfo.jr-central.co.jp/shinkansen/var/train_info/service_status.json"

# LINE Messaging API
LINE_API_URL = "https://api.line.me/v2/bot/message/push"

# 状態保存ファイル
STATE_FILE = "state.json"

# status/cause の日本語マッピング（ti01f_ja.json より）
STATUS_MAP = {
    "1": "遅延",
    "2": "運転見合わせ",
}
CAUSE_MAP = {
    "1": "平常運転", "2": "非常停止ボタン", "3": "人が触車",
    "4": "線路内人立入り", "5": "飛来物", "6": "お客様対応",
    "7": "接続待ち", "8": "車内点検", "9": "停電",
    "10": "電力設備点検", "11": "地震", "12": "架線断線",
    "13": "停電／倒木", "14": "停電／倒竹", "15": "停電／飛来物",
    "16": "安全確認", "17": "車両点検", "18": "雨規制",
    "19": "河川増水", "20": "雪規制", "21": "雪／倒木",
    "22": "雪／倒竹", "23": "ポイント不転換", "24": "風規制",
    "25": "風／飛来物", "26": "風／倒木", "27": "倒木",
    "28": "風／倒竹", "29": "倒竹", "30": "台風",
    "31": "設備点検", "32": "信号設備点検", "33": "線路設備点検",
    "34": "沿線火災", "35": "通信設備点検", "36": "システム点検",
    "37": "トンネル点検", "38": "トンネル崩落", "39": "可動柵点検",
    "40": "異音感知", "41": "乗務員体調不良", "42": "車両交換",
    "43": "他路線の遅れ", "44": "動物と衝撃", "45": "線路内支障物",
    "46": "線路陥没", "47": "不審物確認", "48": "不発弾処理",
    "49": "ミサイル発射情報", "50": "迷惑行為", "51": "テロ行為",
    "52": "霧", "53": "雷", "54": "竜巻", "55": "降灰",
    "56": "黄砂", "57": "視界不良", "58": "台風接近",
    "59": "発煙", "60": "津波", "61": "津波警報",
    "62": "大津波警報", "63": "夜間工事遅れ", "64": "保守用車両脱線",
    "65": "保守用車点検", "66": "電力供給制限", "67": "お客様混雑",
}


# ─── 状態管理 ─────────────────────────────────────────────
def load_state() -> dict:
    """前回の遅延状態を読み込む"""
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"was_abnormal": False}


def save_state(state: dict) -> None:
    """現在の遅延状態を保存する"""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


# ─── JR東海 API ───────────────────────────────────────────
def fetch_service_status() -> dict:
    """
    JR東海の運行情報JSONを取得して返す。
    セッションクッキーを取得するためメインページに先にアクセスする。
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
        ),
        "Referer": JR_MAIN_URL,
        "Accept": "application/json, */*",
    }

    session = requests.Session()
    # セッションクッキーを取得
    session.get(JR_MAIN_URL, headers=headers, timeout=30)
    # 運行情報JSONを取得
    resp = session.get(JR_API_URL, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


def is_abnormal(data: dict) -> bool:
    """遅延・運転見合わせなどの異常が発生しているか判定する"""
    info = data.get("serviceStatusInfo", {})
    return (
        info.get("serviceStatusIsEnabled", False)
        or data.get("suspensionInfoIsEnabled", False)
    )


def build_detail_text(data: dict) -> str:
    """遅延情報の詳細テキストを生成する"""
    lines = []
    info = data.get("serviceStatusInfo", {})

    for item in info.get("data", []):
        status_key = str(item.get("status", ""))
        cause_key  = str(item.get("cause", ""))
        status_str = STATUS_MAP.get(status_key, f"状況({status_key})")
        cause_str  = CAUSE_MAP.get(cause_key,  f"原因({cause_key})")

        station = item.get("station")
        if station:
            start = station.get("start", "")
            end   = station.get("end", "")
            lines.append(f"区間: {start}〜{end}")

        lines.append(f"状況: {status_str}")
        lines.append(f"原因: {cause_str}")

        remarks = item.get("remark", [])
        for r in remarks:
            remark_text = r if isinstance(r, str) else str(r)
            if remark_text:
                lines.append(f"　{remark_text}")

        lines.append("")  # 区切り

    if data.get("suspensionInfoIsEnabled"):
        lines.append("⚠️ 運転見合わせ情報あり")

    return "\n".join(lines).strip()


# ─── LINE 通知 ────────────────────────────────────────────
def send_line_message(text: str) -> None:
    """LINE Messaging API でプッシュ通知を送信する"""
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
    resp.raise_for_status()
    print(f"LINE送信完了: {resp.status_code}")


# ─── メイン処理 ───────────────────────────────────────────
def main() -> None:
    now_str = datetime.now(JST).strftime("%Y/%m/%d %H:%M")

    # 前回の状態を読み込み
    state = load_state()
    was_abnormal = state.get("was_abnormal", False)

    # JR東海 API から最新の運行情報を取得
    print("運行情報を取得中...")
    data = fetch_service_status()
    current_abnormal = is_abnormal(data)

    print(f"遅延状態: {'異常あり' if current_abnormal else '平常運転'} (前回: {'異常あり' if was_abnormal else '平常運転'})")

    # 状態が変化した場合のみ通知
    if current_abnormal and not was_abnormal:
        # 平常 → 遅延：遅延発生通知
        detail = build_detail_text(data)
        message = (
            f"🚨 東海道新幹線 遅延・運行障害情報\n"
            f"確認時刻: {now_str}\n\n"
            f"{detail}\n\n"
            f"詳細: {JR_MAIN_URL}"
        )
        print("遅延発生を検知。LINE通知を送信します。")
        send_line_message(message)

    elif not current_abnormal and was_abnormal:
        # 遅延 → 平常：回復通知
        message = (
            f"✅ 東海道新幹線 運行回復\n"
            f"確認時刻: {now_str}\n\n"
            f"運行が概ね平常に戻りました。\n"
            f"詳細: {JR_MAIN_URL}"
        )
        print("運行回復を検知。LINE通知を送信します。")
        send_line_message(message)

    else:
        print("状態変化なし。通知不要。")

    # 状態を保存
    save_state({"was_abnormal": current_abnormal})


if __name__ == "__main__":
    main()
