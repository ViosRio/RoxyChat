#
#
#-----------CREDITS -----------
# telegram : @legend_coder
# github : noob-mukesh
# Powered by DeepSeek ❤️‍🔥

import os
import json
from pathlib import Path
from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
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
user_friends = {}  # Arkadaş listesi için

# Başlangıç Mesajı
def get_start_message(user):
    emoji = choice(["🔥", "❤️", "🌹", "🎯"])
    private_status = "✅ AÇIK" if private_mode.get(user.id, False) else "❌ KAPALI"
    return f"""
✨ **RoxyMask - Anonim Sohbet Botu** ✨

{emoji} **Gizlilik Ve Eğlence Bir Arada!**

▸ **Eşleş** Butonuyla Rastgele Biriyle Sohbet Et
▸ **Gizli Mod:** {private_status}
▸ **Arkadaş Sayısı:** {len(user_friends.get(user.id, []))}

• Komutlar:
• /start = Botu başlat
• /private = Gizli modu aç/kapat
• /add = Arkadaş ekle
• /list = Arkadaş listesi
• /settings = Ayarlar

Powered by DeepSeek ❤️‍🔥
"""

# Butonlar
MAIN_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("🌟 EŞLEŞ", callback_data="find_partner")],
    [
        InlineKeyboardButton("📜 Yardım", callback_data="help"),
        InlineKeyboardButton("⚙️ Ayarlar", callback_data="settings")
    ],
    [
        InlineKeyboardButton("👥 Arkadaşlar", callback_data="friends"),
        InlineKeyboardButton("👤 Kurucu", url=f"https://t.me/{OWNER_USERNAME}")
    ]
])

SETTINGS_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔒 Gizli Mod Aç/Kapat", callback_data="toggle_private")],
    [InlineKeyboardButton("🔙 Geri", callback_data="back_to_main")]
])

FRIENDS_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("➕ Arkadaş Ekle", callback_data="add_friend")],
    [InlineKeyboardButton("📋 Arkadaş Listesi", callback_data="list_friends")],
    [InlineKeyboardButton("🔙 Geri", callback_data="back_to_main")]
])

# Handler'lar
@app.on_message(filters.command("start"))
async def start(client, message):
    user = message.from_user
    if user.id not in user_friends:
        user_friends[user.id] = []
    await message.reply_photo(
        photo=START_IMG,
        caption=get_start_message(user),
        reply_markup=MAIN_BUTTONS
    )

@app.on_message(filters.command("settings"))
async def settings(client, message):
    await message.reply("⚙️ **Ayarlar**", reply_markup=SETTINGS_BUTTONS)

@app.on_message(filters.command("private"))
async def toggle_private(client, message):
    user_id = message.from_user.id
    private_mode[user_id] = not private_mode.get(user_id, False)
    status = "açıldı" if private_mode[user_id] else "kapatıldı"
    await message.reply(f"🔒 Gizli mod {status}!")

@app.on_message(filters.command("add"))
async def add_friend(client, message):
    if len(message.command) > 1:
        friend_id = message.command[1]
        if message.from_user.id not in user_friends:
            user_friends[message.from_user.id] = []
        if friend_id not in user_friends[message.from_user.id]:
            user_friends[message.from_user.id].append(friend_id)
            await message.reply(f"✅ Arkadaş Eklendi: {friend_id}")
        else:
            await message.reply("⚠️ Bu kullanıcı Zaten Arkadaş Listenizde!")
    else:
        await message.reply("Kullanım: /add CEREN")

@app.on_message(filters.command("list"))
async def list_friends(client, message):
    friends = user_friends.get(message.from_user.id, [])
    if friends:
        await message.reply(f"👥 Arkadaşlarınız:\n" + "\n".join(friends))
    else:
        await message.reply("Arkadaş Listeniz Boş 😢")

# Callback Query Handler
@app.on_callback_query()
async def callback_handler(client, query: CallbackQuery):
    user = query.from_user
    data = query.data
    
    if data == "find_partner":
        if user.id in active_chats:
            await query.answer("Zaten Bir Sohbettesiniz!", show_alert=True)
            return
        
        # Eşleşme işlemi
        if waiting_users:
            partner_id = next(iter(waiting_users))
            active_chats[user.id] = partner_id
            active_chats[partner_id] = user.id
            del waiting_users[partner_id]
            
            await client.send_message(partner_id, "✅ Eşleşme Bulundu! Artık Sohbet Edebilirsiniz.")
            await query.answer("✅ Eşleşme bulundu! Artık Sohbet Edebilirsiniz.", show_alert=True)
        else:
            waiting_users[user.id] = True
            await query.answer("🔎 Eşleşme Aranıyor... Lütfen Bekleyin.", show_alert=True)
    
    elif data == "settings":
        await query.edit_message_text("⚙️ **Ayarlar**", reply_markup=SETTINGS_BUTTONS)
    
    elif data == "toggle_private":
        private_mode[user.id] = not private_mode.get(user.id, False)
        status = "açıldı" if private_mode[user.id] else "kapatıldı"
        await query.answer(f"Gizli mod {status}!")
        await query.edit_message_text("⚙️ **Ayarlar**", reply_markup=SETTINGS_BUTTONS)
    
    elif data == "friends":
        await query.edit_message_text("👥 **Arkadaşlar**", reply_markup=FRIENDS_BUTTONS)
    
    elif data == "add_friend":
        await query.answer("Arkadaş eklemek için: /add CEREN", show_alert=True)
    
    elif data == "list_friends":
        friends = user_friends.get(user.id, [])
        if friends:
            await query.edit_message_text(f"👥 Arkadaşlarınız:\n" + "\n".join(friends))
        else:
            await query.answer("Arkadaş Listeniz Boş 😢", show_alert=True)
    
    elif data == "back_to_main":
        await query.edit_message_text(get_start_message(user), reply_markup=MAIN_BUTTONS)
    
    elif data == "help":
        await query.answer(get_start_message(user), show_alert=True)

def is_not_command(_, __, m: Message):
    return not m.text.startswith('/')

@app.on_message(filters.text & filters.create(is_not_command))
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
            logger.error(f"Mesaj İletme Hatası: {e}")

# Botu Başlat
if __name__ == "__main__":
    print("✨ Bot başlatılıyor...")
    try:
        app.run()
    except Exception as e:
        logger.error(f"Bot hatası: {e}")
