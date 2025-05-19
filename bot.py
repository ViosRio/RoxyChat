#-----------CREDITS -----------
# telegram : @legend_coder
# github : noob-mukesh
# Powered by DeepSeek ❤️‍🔥

import os
import json
from pyrogram import Client, filters
from config import *
from pathlib import Path
from pyrogram import Client, filters, enums, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
import asyncio
from random import choice
from datetime import datetime
import logging

# 1. ÖNCE CLIENT TANIMI (TÜM HANDLERLARDAN ÖNCE GELMELİ)
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

# ... (Diğer tüm fonksiyonlar aynı şekilde kalacak) ...

# Botu Başlat
if __name__ == "__main__":
    print(f"🔥 {BOT_NAME} çalışıyor...")
    try:
        Roxy.start()
        idle()
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        Roxy.stop()

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
        
        # Eşleşme kontrolü
        if len(waiting_users) >= 2:
            partner_id = next((uid for uid in waiting_users if uid != user_id), None)
            
            if partner_id:
                # Eşleşmeyi kaydet
                active_chats[user_id] = partner_id
                active_chats[partner_id] = user_id
                
                # Kullanıcı adlarını al
                user1_name = "❤️ GİZLİ" if private_mode.get(user_id, False) else f"@{waiting_users[user_id]}"
                user2_name = "❤️ GİZLİ" if private_mode.get(partner_id, False) else f"@{waiting_users[partner_id]}"
                
                # Bildirim gönder
                buttons = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Sohbeti Bitir", callback_data="stop_chat")]])
                
                await client.send_message(
                    user_id,
                    f"🎉 **Eşleşme bulundu!**\n\n▸ Partner: {user2_name}\n▸ Mesaj göndermeye başlayabilirsin!",
                    reply_markup=buttons
                )
                
                await client.send_message(
                    partner_id,
                    f"🎉 **Eşleşme bulundu!**\n\n▸ Partner: {user1_name}\n▸ Mesaj göndermeye başlayabilirsin!",
                    reply_markup=buttons
                )
                
                # Bekleme listesinden çıkar
                waiting_users.pop(user_id, None)
                waiting_users.pop(partner_id, None)
                return
        
        # Eşleşme bulunamazsa bekleme mesajı
        buttons = InlineKeyboardMarkup([[InlineKeyboardButton("❌ İptal", callback_data="cancel_wait")]])
        msg = await client.send_message(
            user_id,
            "⏳ **Eşleşme aranıyor... (60 saniye)**",
            reply_markup=buttons
        )
        
        # 60 saniye bekle
        await asyncio.sleep(60)
        
        if user_id in waiting_users:
            await msg.edit("⚠️ Eşleşme bulunamadı. Tekrar deneyin!")
            waiting_users.pop(user_id, None)
            
    except Exception as e:
        logger.error(f"Match users error: {e}")
        if user_id in waiting_users:
            waiting_users.pop(user_id, None)
        await client.send_message(user_id, "⚠️ Bir hata oluştu. Lütfen tekrar deneyin!")

# Mesaj İletme
@Roxy.on_message(filters.text & ~filters.command)
async def forward_message(client, message):
    user_id = message.from_user.id
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        try:
            if private_mode.get(user_id, False):
                await client.send_message(partner_id, f"❤️ GİZLİ: {message.text}")
            else:
                await client.send_message(partner_id, f"@{message.from_user.username}: {message.text}")
        except Exception as e:
            logger.error(f"Message forward error: {e}")
            await message.reply("⚠️ Mesaj gönderilemedi. Partner sohbeti sonlandırmış olabilir.")

# Komutlar
@Roxy.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_photo(
        photo=START_IMG,
        caption=get_start_message(),
        reply_markup=MAIN_BUTTONS
    )

@Roxy.on_callback_query()
async def callback_handler(client, query):
    data = query.data
    user_id = query.from_user.id
    
    try:
        if data == "talking":
            await query.answer("Eşleşme aranıyor...")
            await match_users(client, user_id)
            
        elif data == "stop_chat":
            partner_id = active_chats.get(user_id)
            if partner_id:
                await client.send_message(partner_id, "❌ Partner sohbeti bitirdi!")
                active_chats.pop(partner_id, None)
            active_chats.pop(user_id, None)
            await query.message.edit("✅ Sohbet sonlandırıldı!")
            
        elif data == "cancel_wait":
            if user_id in waiting_users:
                waiting_users.pop(user_id, None)
                await query.message.edit("❌ Eşleşme iptal edildi!")
                
        elif data == "help":
            await query.message.edit(
                HELP_TEXT,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Geri", callback_data="back")]])
            )
            
        elif data == "back":
            await query.message.edit(
                get_start_message(),
                reply_markup=MAIN_BUTTONS
            )
                
    except Exception as e:
        logger.error(f"Callback error: {e}")
        await query.answer("⚠️ Bir hata oluştu!")

@Roxy.on_message(filters.command("add"))
async def add_friend(client, message):
    try:
        if len(message.command) < 2:
            await message.reply("⚠️ Kullanım: /add [kullanıcı_id]")
            return
            
        friend_id = message.command[1]
        if save_friend(message.from_user.id, friend_id):
            await message.reply(f"✅ Arkadaş eklendi: {friend_id}")
        else:
            await message.reply("⚠️ Bu kullanıcı zaten listenizde!")
    except Exception as e:
        logger.error(f"Add friend error: {e}")
        await message.reply("⚠️ Geçersiz ID veya bir hata oluştu!")

@Roxy.on_message(filters.command("list"))
async def list_friends(client, message):
    try:
        friends = get_friends(message.from_user.id)
        if not friends:
            await message.reply("📌 Arkadaş listeniz boş.")
            return
            
        text = "📜 **Arkadaş Listesi:**\n\n" + "\n".join(f"▸ {uid}" for uid in friends)
        await message.reply(text)
    except Exception as e:
        logger.error(f"List friends error: {e}")
        await message.reply("⚠️ Arkadaş listesi alınamadı!")

@Roxy.on_message(filters.command("private"))
async def toggle_private(client, message):
    user_id = message.from_user.id
    private_mode[user_id] = not private_mode.get(user_id, False)
    status = "AÇIK 🔒" if private_mode[user_id] else "KAPALI 🔓"
    await message.reply(f"🕶️ **Gizli Mod:** {status}")

# Botu Başlat
if __name__ == "__main__":
    print(f"🔥 {BOT_NAME} çalışıyor...")
    try:
        Roxy.start()
        idle()
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        Roxy.stop()

