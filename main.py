import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from uvicorn.config import Config
from uvicorn.server import Server
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from cogs.websocket_manager import ws_manager

# .envファイルから環境変数を読み込む
load_dotenv()

# Discord botの設定
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.reactions = True  # リアクションイベントを受信するために必要

bot = commands.Bot(command_prefix='!', intents=intents)
app = FastAPI()



origins = [
    "http://localhost:3000",  # フロントエンドのURLを追加
    "http://localhost:3001",  # フロントエンドのURLを追加
    "https://dao.andbeyondcompany.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/takeakari/image/url")
async def websocket_endpoint(websocket: WebSocket):
    """✅リアクションが押された画像のURLをリアルタイムで送信するWebSocketエンドポイント"""
    await ws_manager.connect(websocket)
    try:
        while True:
            # クライアントからのメッセージを受信(接続維持のため)
            data = await websocket.receive_text()
            print(f"📨 クライアントからのメッセージ: {data}")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
        print("🔌 クライアントが切断されました")
    except Exception as e:
        print(f"❌ WebSocketエラー: {e}")
        ws_manager.disconnect(websocket)


@bot.event
async def on_ready():
    print(f'{bot.user} としてログインしました')
    print(f'Bot ID: {bot.user.id}')
    print('------')
    

@bot.event
async def setup_hook():
    await bot.load_extension("cogs.removebg")

    

# Botを起動
async def start_services():
    # FastAPI用のサーバーインスタンスを作成
    config = Config(app=app, host="0.0.0.0", port=4444,
                    loop="asyncio", reload=False, workers=3)
    server = Server(config)
    token = os.getenv('DISCORD_BOT_TOKEN')
    

    # BotとAPIサーバーを並列起動
    await asyncio.gather(
        # ← 自分のBotトークンに置き換えてください
        bot.start(token),
        server.serve()
    )

# 実行
if __name__ == "__main__":
    asyncio.run(start_services())