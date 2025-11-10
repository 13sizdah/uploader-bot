"""هندلر استارت و منوی اصلی"""

from pyrogram import Client, filters
from pyrogram.types import Message
from database.db import db
from keyboards.user import main_menu
from keyboards.admin import admin_panel
from config import config
import time

@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    """هندلر استارت"""
    user_id = message.from_user.id
    
    # بررسی بلاک بودن
    user = db.fetchone('SELECT * FROM users WHERE user_id = ?', (user_id,))
    if user and user['is_blocked']:
        await message.reply_text("⛔️ شما از استفاده از ربات محروم شده‌اید!")
        return
    
    # بررسی وضعیت ربات
    bot_status = db.fetchone('SELECT value FROM settings WHERE key = ?', ('bot_status',))
    if bot_status and bot_status['value'] == 'off':
        if user_id not in config.ADMIN_IDS:
            await message.reply_text("🔧 ربات در حال تعمیر و نگهداری است\nلطفاً بعداً تلاش کنید")
            return
    
    # ثبت/به‌روزرسانی کاربر
    if not user:
        db.execute('''
            INSERT INTO users (user_id, username, first_name, joined_at, last_activity)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            user_id,
            message.from_user.username,
            message.from_user.first_name,
            int(time.time()),
            int(time.time())
        ))
    else:
        db.execute('''
            UPDATE users 
            SET username = ?, first_name = ?, last_activity = ?
            WHERE user_id = ?
        ''', (
            message.from_user.username,
            message.from_user.first_name,
            int(time.time()),
            user_id
        ))
    
    # بررسی جوین اجباری
    if config.FORCE_JOIN:
        from utils.helpers import check_user_joined
        joined, not_joined_channels = await check_user_joined(client, user_id)
        
        if not joined and user_id not in config.ADMIN_IDS:
            text = "⚠️ برای استفاده از ربات باید در کانال‌های زیر عضو شوید:\n\n"
            
            for channel in not_joined_channels:
                text += f"🔹 @{channel['channel_username']}\n"
            
            text += "\nبعد از عضویت دوباره /start را بزنید"
            await message.reply_text(text)
            return
    
    # نمایش منوی مناسب
    from utils.helpers import is_premium, format_number
    
    user = db.fetchone('SELECT * FROM users WHERE user_id = ?', (user_id,))
    
    text = config.START_MESSAGE.format(
        free_downloads=config.FREE_DOWNLOAD_LIMIT - user['daily_downloads']
    )
    
    if is_premium(user_id):
        text += f"\n\n💎 **اشتراک شما فعال است**\n"
        remain_days = (user['subscription_end'] - int(time.time())) // 86400
        text += f"⏳ باقیمانده: {remain_days} روز"
    
    if user_id in config.ADMIN_IDS:
        keyboard = admin_panel()
    else:
        keyboard = main_menu()
    
    await message.reply_text(text, reply_markup=keyboard)

@Client.on_message(filters.regex("^🔙 بازگشت به منوی اصلی$") & filters.private)
async def back_to_main(client: Client, message: Message):
    """بازگشت به منو"""
    await start_handler(client, message)
