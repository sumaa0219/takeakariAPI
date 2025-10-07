from fastapi import WebSocket, WebSocketDisconnect
from typing import Set
import json


class WebSocketManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        print(f"✅ WebSocket接続が確立されました。アクティブな接続数: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        print(f"❌ WebSocket接続が切断されました。アクティブな接続数: {len(self.active_connections)}")
    
    async def broadcast_image_url(self, image_url: str, message_id: int, channel_id: int):
        """✅リアクションが押された画像のURLを全接続に送信（文字列のみ）"""
        if not self.active_connections:
            print("⚠️ アクティブなWebSocket接続がありません")
            return
        
        disconnected = set()
        for connection in self.active_connections:
            try:
                # 画像URLの文字列のみを送信
                await connection.send_text(image_url)
                print(f"📤 画像URLを送信しました: {image_url}")
            except Exception as e:
                print(f"❌ 送信エラー: {e}")
                disconnected.add(connection)
        
        # 切断されたコネクションを削除
        for connection in disconnected:
            self.disconnect(connection)


# グローバルなWebSocketマネージャーインスタンス
ws_manager = WebSocketManager()
