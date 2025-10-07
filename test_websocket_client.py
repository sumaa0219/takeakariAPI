"""
WebSocketテストクライアント
Discord Botから送信される画像URLを受信するテストクライアント
"""
import asyncio
import websockets
import json


async def test_websocket_client():
    uri = "ws://localhost:4444/takeakari/image/url"
    
    print("🔌 WebSocketサーバーに接続中...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocketサーバーに接続しました!")
            print("⏳ Discord内で画像に✅リアクションをつけると、ここにURLが表示されます...\n")
            
            # 接続維持のために定期的にpingを送信
            async def send_ping():
                while True:
                    await asyncio.sleep(30)
                    await websocket.send(json.dumps({"type": "ping"}))
            
            # pingタスクを開始
            ping_task = asyncio.create_task(send_ping())
            
            try:
                # メッセージを受信し続ける
                while True:
                    message = await websocket.recv()
                    # 画像URLの文字列として受信
                    image_url = message
                    
                    print("=" * 60)
                    print("📸 新しい画像が承認されました!")
                    print(f"画像URL: {image_url}")
                    print("=" * 60 + "\n")
            except asyncio.CancelledError:
                ping_task.cancel()
                raise
                
    except ConnectionRefusedError:
        print("❌ サーバーに接続できませんでした。")
        print("   バックエンドサーバーが起動しているか確認してください。")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")


if __name__ == "__main__":
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  WebSocket画像URL受信テスト")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    
    try:
        asyncio.run(test_websocket_client())
    except KeyboardInterrupt:
        print("\n\n👋 接続を終了しました。")
