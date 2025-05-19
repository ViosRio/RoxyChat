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

# 1. ÖNCE CLIENT TANIMI (EN ÜSTTE OLMALI)
Roxy = Client(
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

HELP_TEXT = """
**📌 Komutlar:**
▸ /start - Botu başlat
▸ /ping - Bot durumunu kontrol et
▸ /add [ID] - Arkadaş ekle
▸ /private - Gizli mod (❤️ GİZLİ)
▸ /list - Arkadaş listesi
▸ /stop - Sohbeti bitir

**🔥 Eşleşme Sistemi:**
1. "EŞLEŞ" butonuna bas
2. Partner bulununca bildirim alacaksın
3. Kimliğin gizli kalacak!

*Powered by DeepSeek ❤️‍🔥*
"""

# JSON işlemleri
def save_friend(user_id, friend_id):
    user_file = LIST_DIR / f"{user_id}.json"
    try:
        data = {"friends": []}
        if user_file.exists():
            with open(user_file, 'r') as f:
                data = json.load(f)
        
        if str(friend_id) not in data["friends"]:
            data["friends"].append(str(friend_id))
            with open(user_file, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        return False
    except Exception as e:
        logger.error(f"Save friend error: {e}")
        return False

def get_friends(user_id):
    user_file = LIST_DIR / f"{user_id}.json"
    if user_file.exists():
        with open(user_file, 'r') as f:
            data = json.load(f)
        return data.get("friends", [])
    return []

# Eşleşme Fonksiyonu
async def match_users(client, user_id):
    try:
        if user_id in waiting_users:
            await client.send_message(user_id, "⏳ Zaten eşleşme arıyorsunuz!")
            return

        me = await client.get_me()
        waiting_users[user_id] = me.username
        
        if len(waiting_users) >= 2:
            partner_id = next((uid for uid in waiting_users if uid != user_id), None)
            
            if partner_id:
                active_chats[user_id] = partner_id
                active_chats[partner_id] = user_id
                
                user1_name = "❤️ GİZLİ" if private_mode.get(user_id, False) else f"@{waiting_users[user_id]}"
                user2_name = "❤️ GİZLİ" if private_mode.get(partner_id, False) else f"@{waiting_users[partner_id]}"
                
                buttons = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Sohbeti Bitir", callback_data="stop_chat")]])
                
                await client.send_message(
                    user_id,
                    f"🎉 **Eşleşme bulundu!**\n\n▸ Partner: {user2_name}",
                    reply_markup=buttons
                )
                await client.send_message(
                    partner_id,
                    f"🎉 **Eşleşme bulundu!**\n\n▸ Partner: {user1_name}",
                    reply_markup=buttons
                )
                
                waiting_users.pop(user_id, None)
                waiting_users.pop(partner_id, None)
                return
        
        buttons = InlineKeyboardMarkup([[InlineKeyboardButton("❌ İptal", callback_data="cancel_wait")]])
        msg = await client.send_message(
            user_id,
            "⏳ **Eşleşme aranıyor... (60 saniye)**",
            reply_markup=buttons
        )
        
        await asyncio.sleep(60)
        
        if user_id in waiting_users:
            await msg.edit("⚠️ Eşleşme bulunamadı. Tekrar deneyin!")
            waiting_users.pop(user_id, None)
            
    except Exception as e:
        logger.error(f"Match error: {e}")
        if user_id in waiting_users:
            waiting_users.pop(user_id, None)
        await client.send_message(user_id, "⚠️ Hata oluştu. Tekrar deneyin!")

# Handler'lar
@Roxy.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_photo(
        photo=START_IMG,
        caption=get_start_message(),
        reply_markup=MAIN_BUTTONS
    )

@Roxy.on_message(filters.text & ~filters.command)
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
            logger.error(f"Forward error: {e}")
            await message.reply("⚠️ Mesaj iletilemedi")

# Diğer handler'lar (callback, add, list, private) aynı şekilde kalacak...

if __name__ == "__main__":
    print("✨ Bot başlatılıyor...")
    try:
        Roxy.start()
        print("✅ Bot çalışıyor! CTRL+C ile durdurabilirsin")
        idle()
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        Roxy.stop()
