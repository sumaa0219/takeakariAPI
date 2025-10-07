# Discord 背景削除Bot + WebSocket画像配信

rembgを使用して、Discordチャンネルに投稿された画像の背景を自動的に削除するBotです。
また、✅リアクションが押された画像のURLをWebSocketでリアルタイム配信する機能も搭載しています。

## 機能

- 特定のチャンネル(または全チャンネル)に投稿された画像を自動検知
- rembgを使用して背景を削除
- 処理済みの画像を元のチャンネルに返信
- 対応画像形式: PNG, JPG, JPEG, WebP
- **🆕 Discord内で✅リアクションが押された画像のURLをWebSocketで配信**

## 必要なもの

- Python 3.8以上
- Discord Bot Token
- 必要なPythonライブラリ(requirements.txtに記載)

## セットアップ

### 1. Discord Botの作成

1. [Discord Developer Portal](https://discord.com/developers/applications)にアクセス
2. "New Application"をクリックして新しいアプリケーションを作成
3. 左メニューから"Bot"を選択
4. "Add Bot"をクリック
5. "TOKEN"セクションで"Reset Token"をクリックしてトークンを取得(このトークンは後で使用します)
6. "Privileged Gateway Intents"セクションで以下を有効化:
   - MESSAGE CONTENT INTENT
   - SERVER MEMBERS INTENT(オプション)
7. 左メニューから"OAuth2" > "URL Generator"を選択
8. "SCOPES"で`bot`を選択
9. "BOT PERMISSIONS"で以下を選択:
   - Send Messages
   - Attach Files
   - Read Message History
   - View Channels
10. 生成されたURLをブラウザで開いてBotをサーバーに追加

### 2. 環境設定

```bash
# リポジトリをクローンまたはダウンロード
cd localink

# 仮想環境を作成(推奨)
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# または
.venv\Scripts\activate  # Windows

# 必要なライブラリをインストール
pip install -r requirements.txt

# .envファイルを作成
cp .env.example .env
```

### 3. .envファイルの編集

`.env`ファイルを開いて、Discord Botのトークンを設定します:

```
DISCORD_BOT_TOKEN=your_actual_discord_bot_token_here
```

### 4. Discord Bot設定の重要な注意点

Discord Developer Portalで以下のIntentsを必ず有効化してください:
- **MESSAGE CONTENT INTENT** - メッセージ内容の取得に必要
- **PRESENCE INTENT** - プレゼンス情報の取得に必要(オプション)
- **SERVER MEMBERS INTENT** - メンバー情報の取得に必要(オプション)
- **Message Reactions** - リアクションイベントの取得に必要(✅機能に必須)

### 5. チャンネルIDの設定(オプション)

特定のチャンネルでのみ背景削除を行いたい場合は、`cogs/removebg.py`の`TARGET_CHANNEL_IDS`リストにチャンネルIDを追加します:

```python
TARGET_CHANNEL_IDS = [123456789012345678, 987654321098765432]  # 実際のチャンネルIDに置き換え
```

チャンネルIDの取得方法:
1. Discordで開発者モードを有効化(設定 > 詳細設定 > 開発者モード)
2. チャンネルを右クリックして"IDをコピー"

空のリスト`[]`のままにすると、全チャンネルで動作します。

## 使用方法

### Botの起動

#### 方法1: Dockerを使用する(推奨)

```bash
# Dockerイメージのビルドとコンテナの起動
docker-compose up -d --build

# ログの確認
docker-compose logs -f

# コンテナの停止
docker-compose down
```

#### 方法2: ローカルで直接実行

```bash
python main.py
```

または仮想環境を使用している場合:

```bash
.venv/bin/python main.py
```

起動に成功すると、以下のようなメッセージが表示されます:
```
BotName#1234 としてログインしました
Bot ID: 1234567890
------
```

### Botの使い方

#### 背景削除機能
1. Botが追加されたDiscordサーバーで、対象のチャンネルに画像を投稿
2. Botが自動的に画像を処理して、背景が削除された画像を返信します
3. `!help_rembg`コマンドでヘルプを表示できます

#### WebSocket画像配信機能(新機能)
1. **WebSocketエンドポイント**: `ws://localhost:4444/takeakari/image/url`
2. Discord内で任意の画像に✅(チェックマーク)リアクションをつける
3. WebSocketクライアントに画像URLがリアルタイムで配信されます

**送信されるデータ形式**:
画像URLの文字列のみが送信されます。
```
https://cdn.discordapp.com/attachments/1234567890/0987654321/image.png
```

#### WebSocketテストクライアントの使用方法

```bash
# テストクライアントを実行
python test_websocket_client.py
```

実行後、Discord内で画像に✅リアクションをつけると、コンソールに画像URLが表示されます。

## トラブルシューティング

### "DISCORD_BOT_TOKENが設定されていません"エラー

- `.env`ファイルが正しく作成されているか確認
- `.env`ファイルにトークンが正しく記載されているか確認

### Botが画像を処理しない

- Botに必要な権限(メッセージを読む、送信する、ファイルを添付する)が付与されているか確認
- `TARGET_CHANNEL_IDS`が設定されている場合、正しいチャンネルIDか確認
- Discord Developer Portalで"MESSAGE CONTENT INTENT"が有効になっているか確認

### 処理が遅い

- rembgは機械学習モデルを使用するため、初回実行時はモデルのダウンロードに時間がかかります
- 大きな画像ほど処理に時間がかかります

## ファイル構成

```
backend/
├── main.py                      # メインのBotスクリプト
├── requirements.txt             # 必要なPythonライブラリ
├── test_websocket_client.py    # WebSocketテストクライアント
├── .env                         # 環境変数(Botトークンを含む)
├── Dockerfile                   # Dockerイメージの定義
├── docker-compose.yml           # Docker Compose設定
├── README.md                    # このファイル
└── cogs/
    ├── removebg.py              # 背景削除 & リアクション検知機能
    └── websocket_manager.py     # WebSocket接続管理
```

## Docker使用時の注意事項

- 初回起動時はrembgのモデル(約176MB)が自動的にダウンロードされます
- ボリュームマウントにより、コード変更後は`docker-compose restart`で反映されます
- `.env`ファイルのトークンは自動的にコンテナ内で利用されます

## ライセンス

このプロジェクトは自由に使用できます。

## 注意事項

- Botトークンは絶対に公開しないでください
- `.env`ファイルをGitにコミットしないでください(`.gitignore`に追加することを推奨)
- rembgの処理には時間がかかる場合があります
- 大量の画像を連続で処理する場合はDiscordのレート制限に注意してください
