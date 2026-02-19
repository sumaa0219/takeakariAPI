from fastapi import APIRouter, HTTPException, Query
from discord.ext import commands
from discord import app_commands
import discord
import io
from rembg import remove
from rembg.session_factory import new_session
from PIL import Image
import aiohttp
import os
from .websocket_manager import ws_manager
# rembgのセッションを作成 (変数名を'rembg_session'に変更してaiohttpのsessionと競合しないように)
rembg_session = new_session("silueta")

# 背景削除を行うチャンネルID(複数指定可能)
TARGET_CHANNEL_IDS = [1423802355782127676]  # 例: [123456789, 987654321]


class RemovebgCog(commands.Cog):
    def __init__(self, bot):  # コンストラクタ
        self.bot = bot
        print("Cog removebg.py init!")


    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog removebg.py ready!")
        if not TARGET_CHANNEL_IDS:
            print('⚠️ 警告: TARGET_CHANNEL_IDsが空です。チャンネルIDを設定してください。')
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """✅リアクションが追加されたときの処理"""
        # ✅エモジ以外は無視
        if str(payload.emoji) != '✅':
            return
        
        # Bot自身のリアクションは無視
        if payload.member and payload.member.bot:
            return
        
        try:
            # メッセージを取得
            channel = self.bot.get_channel(payload.channel_id)
            if not channel:
                return
            
            message = await channel.fetch_message(payload.message_id)
            
            # メッセージに添付ファイル(画像)がある場合
            if message.attachments:
                for attachment in message.attachments:
                    # 画像ファイルのみ処理
                    if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.webp']):
                        print(f"✅ リアクション検知: {attachment.url}")
                        # WebSocketで画像URLを送信
                        await ws_manager.broadcast_image_url(
                            image_url=str(attachment.url),
                            message_id=payload.message_id,
                            channel_id=payload.channel_id
                        )
            
            # メッセージに埋め込み画像がある場合
            elif message.embeds:
                for embed in message.embeds:
                    if embed.image:
                        print(f"✅ リアクション検知(Embed): {embed.image.url}")
                        await ws_manager.broadcast_image_url(
                            image_url=embed.image.url,
                            message_id=payload.message_id,
                            channel_id=payload.channel_id
                        )
        
        except Exception as e:
            print(f"❌ リアクション処理中にエラーが発生: {e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        # Bot自身のメッセージは無視
        if message.author.bot:
            return
        
        # 対象チャンネル以外は無視(TARGET_CHANNEL_IDsが空の場合は全チャンネル対象)
        if TARGET_CHANNEL_IDS and message.channel.id not in TARGET_CHANNEL_IDS:
            return
        
        # 添付ファイルがある場合のみ処理
        if message.attachments:
            for attachment in message.attachments:
                # 画像ファイルのみ処理
                if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.webp']):
                    try:
                        # 処理中メッセージを送信
                        processing_msg = await message.channel.send(f'🔄 画像を処理中... ({attachment.filename})')
                        
                        # 画像をダウンロード
                        async with aiohttp.ClientSession() as session:
                            async with session.get(attachment.url) as resp:
                                if resp.status == 200:
                                    image_data = await resp.read()
                                else:
                                    await processing_msg.edit(content='❌ 画像のダウンロードに失敗しました。')
                                    continue
                        
                        # 背景を削除
                        input_image = Image.open(io.BytesIO(image_data))
                        output_image = remove(input_image, session=rembg_session)
                        
                        # 出力画像をバイトデータに変換
                        output_buffer = io.BytesIO()
                        output_image.save(output_buffer, format='PNG')
                        output_buffer.seek(0)
                        
                        # ファイル名を生成(元のファイル名 + _nobg.png)
                        original_name = os.path.splitext(attachment.filename)[0]
                        output_filename = f'{original_name}_nobg.png'
                        
                        # 処理済み画像を送信
                        await message.channel.send(
                            content=f'✅ 背景削除が完了しました！',
                            file=discord.File(fp=output_buffer, filename=output_filename)
                        )
                        
                        # 処理中メッセージを削除
                        await processing_msg.delete()
                        
                    except Exception as e:
                        print(f'エラーが発生しました: {e}')
                        await message.channel.send(f'❌ 処理中にエラーが発生しました: {str(e)}')
        
        # コマンドの処理を継続
        await self.bot.process_commands(message)
        
        
    @app_commands.command(name='help_rembg', description='背景削除Botのヘルプを表示')
    async def help_command(self, interaction: discord.Interaction):
        """ヘルプメッセージを表示"""
        embed = discord.Embed(
            title='📖 背景削除Bot - 使い方',
            description='このBotは画像の背景を自動的に削除します。',
            color=discord.Color.blue()
        )
        embed.add_field(
            name='使用方法',
            value='画像を添付してメッセージを送信するだけで、自動的に背景が削除された画像が返信されます。',
            inline=False
        )
        embed.add_field(
            name='対応形式',
            value='PNG, JPG, JPEG, WebP',
            inline=False
        )
        embed.add_field(
            name='コマンド',
            value='`/help_rembg` - このヘルプを表示',
            inline=False
        )
        
        if TARGET_CHANNEL_IDS:
            channels = ', '.join([f'<#{channel_id}>' for channel_id in TARGET_CHANNEL_IDS])
            embed.add_field(
                name='対象チャンネル',
                value=channels,
                inline=False
            )
        else:
            embed.add_field(
                name='対象チャンネル',
                value='全チャンネル',
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)


# Cogをセットアップする関数
async def setup(bot):
    await bot.add_cog(RemovebgCog(bot))

