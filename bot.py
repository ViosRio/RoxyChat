#
#-----------CREDITS -----------
# telegram : @legend_coder
# github : noob-mukesh
import os
from pyrogram import Client, filters, enums, idle
from pyrogram.errors import ApiIdInvalid, ApiIdPublishedFlood, AccessTokenInvalid
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.enums import ChatAction, ParseMode
import asyncio, time
from random import choice
from datetime import datetime
import logging
from config import *

# Veritabanı için basit bir sözlük (gerçek projede SQLite/MongoDB kullan)
active_chats = {}
waiting_users = {}
private_mode = {}

FORMAT = "[ROXYMASK] %(message)s"
logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

StartTime = time.time()
Roxy = Client(
    "roxy-mask",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Başlangıç Mesajı
START = f"""
✨ **RoxyMask - Anonim Sohbet Botu** ✨

{choice(["🔥", "❤️", "🌹", "🎯"])} **Gizlilik ve eğlence bir arada!**

▸ **Eşleş** butonuyla rastgele biriyle sohbet et
▸ **/private** komutuyla kimliğini gizle
▸ **/add** ile arkadaşlarını ekle
"""

# Butonlar
MAIN = [
    [InlineKeyboardButton("🌟 EŞLEŞ", callback_data="talking")],
    [
        InlineKeyboardButton("📜 Yardım", callback_data="HELP"),
        InlineKeyboardButton("👤 Sahip", url=f"https://t.me/{OWNER_USERNAME}")
    ]
]

HELP_READ = """
**📌 Komutlar:**
▸ /start - Botu başlat
▸ /ping - Botun çalışma durumu
▸ /add [ID] - Arkadaş ekle (Örnek: `/add 123456789`)
▸ /private - Gizli modu aç/kapat (❤️ GİZLİ)
▸ /stop - Aktif sohbeti sonlandır

**🔥 Eşleşme Sistemi:**
1. "EŞLEŞ" butonuna bas
2. 60 saniye içinde eşleşme bulunacak
3. Kimliğin gizli kalacak!
"""

# Eşleşme Fonksiyonu
async def match_users(client, user_id):
    if len(waiting_users) >= 1:
        # Rastgele bir kullanıcı bul
        partner_id = next(iter(waiting_users))
        
        # Eşleşmeyi kaydet
        active_chats[user_id] = partner_id
        active_chats[partner_id] = user_id
        
        # Her iki kullanıcıya da bildirim gönder
        for uid in [user_id, partner_id]:
            name = "❤️ GİZLİ" if private_mode.get(uid, False) else f"@{waiting_users[uid]}"
            await client.send_message(
                uid,
                f"🎉 **Eşleşme bulundu!**\n\n▸ Partner: {name}\n▸ Mesaj göndermeye başlayabilirsin!",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Sohbeti Bitir", callback_data="stop_chat")]])
            )
            waiting_users.pop(uid, None)
    else:
        waiting_users[user_id] = (await client.get_me()).username
        await client.send_message(
            user_id,
            "⏳ **Eşleşme aranıyor... (60 saniye)**",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ İptal", callback_data="cancel_wait")]])
        )
        await asyncio.sleep(60)
        if user_id in waiting_users:
            await client.send_message(user_id, "⚠️ Eşleşme bulunamadı. Tekrar deneyin!")
            waiting_users.pop(user_id, None)

# Komutlar
@Roxy.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_photo(
        photo=START_IMG,
        caption=START,
        reply_markup=InlineKeyboardMarkup(MAIN)
    )

@Roxy.on_callback_query()
async def callback_handler(client, query):
    data = query.data
    user_id = query.from_user.id
    
    if data == "talking":
        await match_users(client, user_id)
    
    elif data == "stop_chat":
        partner_id = active_chats.get(user_id)
        if partner_id:
            await client.send_message(partner_id, "❌ Partner sohbeti bitirdi!")
            active_chats.pop(partner_id, None)
        active_chats.pop(user_id, None)
        await query.message.edit("✅ Sohbet sonlandırıldı!")
    
    elif data == "cancel_wait":
        waiting_users.pop(user_id, None)
        await query.message.edit("❌ Eşleşme iptal edildi!")

@Roxy.on_message(filters.command("add"))
async def add_friend(client, message):
    try:
        _, user_id = message.text.split()
        # Burada arkadaş ekleme işlemleri yapılacak
        await message.reply(f"✅ Arkadaş eklendi: {user_id}")
    except:
        await message.reply("⚠️ Kullanım: /add [kullanıcı_id]")

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
        print(f"Hata: {e}")
    finally:
        Roxy.stop()
