#
#-----------CREDITS -----------
# telegram : @legend_coder
# github : noob-mukesh
# Powered by DeepSeek ❤️‍🔥

import os
import json
from pathlib import Path
from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
import asyncio
from random import choice
import logging
from config import *

# 1. CLIENT TANIMI (EN ÜSTTE)
app = Client(
    "roxy-mask",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Log ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Veritabanı klasörü
DATA_DIR = Path("data")
LIST_DIR = DATA_DIR / "list"
LIST_DIR.mkdir(parents=True, exist_ok=True)

# Global değişkenler
active_chats = {}
waiting_users = {}
private_mode = {}

# Başlangıç Mesajı
def get_start_message():
    emoji = choice(["🔥", "❤️", "🌹", "🎯"])
    return f"""
✨ **RoxyMask - Anonim Sohbet Botu** ✨

{emoji} **Gizlilik ve eğlence bir arada!**

▸ **Eşleş** butonuyla rastgele biriyle sohbet et
▸ **/private** komutuyla kimliğini gizle
▸ **/add** ile arkadaşlarını ekle
▸ **/list** ile arkadaş listesini gör

*Powered by DeepSeek ❤️‍🔥*
"""

# Butonlar
MAIN_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("🌟 EŞLEŞ", callback_data="talking")],
    [
        InlineKeyboardButton("📜 Yardım", callback_data="help"),
        InlineKeyboardButton("👤 Sahip", url=f"https://t.me/{OWNER_USERNAME}")
    ]
])

# Handler'lar
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_photo(
        photo=START_IMG,
        caption=get_start_message(),
        reply_markup=MAIN_BUTTONS
    )

@app.on_message(filters.text & ~filters.command)
async def forward_msg(client, message):
    user_id = message.from_user.id
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        try:
            if private_mode.get(user_id, False):
                await client.send_message(partner_id, f"❤️ GİZLİ: {message.text}")
            else:
                await client.send_message(partner_id, f"@{message.from_user.username}: {message.text}")
        except Exception as e:
            logger.error(f"Mesaj iletme hatası: {e}")

# Botu Başlat
if __name__ == "__main__":
    print("✨ Bot başlatılıyor...")
    try:
        app.run()
    except Exception as e:
        logger.error(f"Bot hatası: {e}")
