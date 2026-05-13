# 東海道新幹線 遅延LINE通知

東海道新幹線（東京〜名古屋間）に遅延・運転見合わせが発生したとき、LINEに自動通知するシステムです。  
GitHub Actions（無料枠）+ LINE Messaging API（無料枠）で動作します。

---

## 仕組み

```
GitHub Actions（10分ごとに起動）
  └─ check_delay.py を実行
       ├─ JR東海の運行情報APIを取得
       ├─ 遅延状態が変化したか判定
       │    変化あり → LINE Messaging API で通知送信
       │    変化なし → 何もしない
       └─ 状態を state.json に保存してコミット
```

**通知タイミング:**
- 平常 → 遅延・障害：🚨 遅延発生の通知
- 遅延・障害 → 平常：✅ 運行回復の通知

---

## セットアップ手順

### ステップ1：GitHubリポジトリを作成

1. [GitHub](https://github.com) にログインし、新しいリポジトリを作成します。  
   **無料で使うには Public（公開）を推奨**（Private は月2,000分の制限あり）
2. このフォルダの内容をそのままリポジトリにプッシュします。

```bash
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/あなたのユーザー名/リポジトリ名.git
git push -u origin main
```

---

### ステップ2：LINE公式アカウントとMessaging APIを設定

#### 2-1. LINE Developersでチャネルを作成

1. [LINE Developers](https://developers.line.biz/ja/) にアクセスし、LINEアカウントでログイン
2. 「プロバイダーを作成」→ 任意の名前を入力（例：`新幹線通知`）
3. 「チャネルを作成」→「Messaging API」を選択
4. 以下を入力して作成：
   - チャネル名：`新幹線遅延通知`（任意）
   - チャネル説明：任意
   - 大業種・小業種：任意
5. 作成後、「Messaging API設定」タブを開く

#### 2-2. チャネルアクセストークンを発行

1. 「Messaging API設定」タブ → 一番下の「チャネルアクセストークン（長期）」
2. 「発行」をクリック → トークン（長い文字列）をコピーして保存

#### 2-3. 自分のLINEと友だちになる

1. 同じ「Messaging API設定」タブの QRコード から自分でBotを友だち追加

#### 2-4. 自分のユーザーIDを取得

1. 「チャネル基本設定」タブ → 「あなたのユーザーID」欄（`Uxxxxxxxxx` の形式）をコピーして保存

---

### ステップ3：GitHubのSecretsに認証情報を登録

1. GitHubリポジトリ → **Settings** → **Secrets and variables** → **Actions**
2. 「New repository secret」で以下の2つを登録：

| Secret名 | 値 |
|---|---|
| `LINE_CHANNEL_ACCESS_TOKEN` | ステップ2-2でコピーしたトークン |
| `LINE_USER_ID` | ステップ2-4でコピーした `Uxxxxxxxxx` |

---

### ステップ4：GitHub Actionsを有効化

1. リポジトリの **Actions** タブを開く
2. ワークフローが表示されたら「I understand my workflows, go ahead and enable them」をクリック
3. **「東海道新幹線 遅延監視」** ワークフローを選択 → 「Run workflow」で手動テスト実行

---

## 動作確認

手動実行後、Actions タブでログを確認してください。

**正常時のログ例:**
```
運行情報を取得中...
遅延状態: 平常運転 (前回: 平常運転)
状態変化なし。通知不要。
```

**LINE通知のサンプル（遅延発生時）:**
```
🚨 東海道新幹線 遅延・運行障害情報
確認時刻: 2026/05/13 12:30

区間: 東京〜名古屋
状況: 遅延
原因: 地震
　発生時刻　12:15

詳細: https://traininfo.jr-central.co.jp/shinkansen/sp/ja/index.html
```

---

## 料金について

| サービス | 無料枠 |
|---|---|
| GitHub Actions（Public リポジトリ） | 無制限 |
| GitHub Actions（Private リポジトリ） | 月2,000分（注） |
| LINE Messaging API | 月200通まで無料 |

> **注:** Private リポジトリで10分ごとに実行すると月約4,320回 → 制限を超えるため、**Public リポジトリ推奨**です。  
> センシティブな情報（トークンなど）はすべてSecretsに保存するため、公開リポジトリでも安全です。

---

## ファイル構成

```
.
├── .github/
│   └── workflows/
│       └── check_delay.yml   # GitHub Actions ワークフロー
├── check_delay.py             # 遅延チェック・通知スクリプト
├── state.json                 # 前回の遅延状態（自動更新）
└── README.md                  # このファイル
```
