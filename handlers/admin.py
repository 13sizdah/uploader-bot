"""هندلرهای پنل ادمین"""

from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from database.db import db
from utils.decorators import admin_only
from keyboards.admin import *
from config import config
import time
import json

# --- آمار کامل ---

@Client.on_message(filters.regex("^📊 آمار کامل$") & filters.private)
@admin_only
async def full_statistics(client: Client, message: Message):
    """نمایش آمار کامل"""
    
    # آمار کاربران
    total_users = db.fetchone('SELECT COUNT(*) as count FROM users')['count']
    premium_users = db.fetchone('SELECT COUNT(*) as count FROM users WHERE is_premium = 1')['count']
    blocked_users = db.fetchone('SELECT COUNT(*) as count FROM users WHERE is_blocked = 1')['count']
    
    # آمار رسانه
    total_media = db.fetchone('SELECT COUNT(*) as count FROM media WHERE is_active = 1')['count']
    total_views = db.fetchone('SELECT SUM(real_views) as total FROM media')['total'] or 0
    total_downloads = db.fetchone('SELECT SUM(real_downloads) as total FROM media')['total'] or 0
    
    # آمار پرداخت
    total_revenue = db.fetchone('''
        SELECT SUM(amount) as total FROM transactions WHERE status = 'completed'
    ''')['total'] or 0
    
    pending_payments = db.fetchone('''
        SELECT COUNT(*) as count FROM transactions WHERE status = 'pending'
    ''')['count']
    
    # آمار امروز
    today_start = int(time.time()) - (int(time.time()) % 86400)
    new_users_today = db.fetchone('''
        SELECT COUNT(*) as count FROM users WHERE joined_at >= ?
    ''', (today_start,))['count']
    
    text = f"""
📊 **آمار کامل ربات**

👥 **کاربران:**
• کل کاربران: {total_users:,}
• اشتراک ویژه: {premium_users:,}
• کاربران مسدود: {blocked_users:,}
• کاربران امروز: {new_users_today:,}

📁 **رسانه‌ها:**
• کل رسانه‌ها: {total_media:,}
• کل بازدیدها: {total_views:,}
• کل دانلودها: {total_downloads:,}

💰 **درآمد:**
• درآمد کل: {total_revenue:,} تومان
• پرداخت‌های در انتظار: {pending_payments}

📅 **تاریخ:** {time.strftime('%Y/%m/%d %H:%M')}
    """
    
    await message.reply_text(text)

# --- مدیریت پوشه‌ها ---

@Client.on_message(filters.regex("^📁 مدیریت پوشه‌ها$") & filters.private)
@admin_only
async def manage_folders(client: Client, message: Message):
    """مدیریت پوشه‌ها"""
    await message.reply_text(
        "📁 **مدیریت پوشه‌ها**\n\n"
        "عملیات مورد نظر را انتخاب کنید:",
        reply_markup=folders_menu()
    )

@Client.on_callback_query(filters.regex(r"^admin_new_folder$"))
@admin_only
async def create_folder(client: Client, callback: CallbackQuery):
    """ساخت پوشه جدید"""
    await callback.message.edit_text(
        "📁 **ساخت پوشه جدید**\n\n"
        "نام پوشه را وارد کنید:"
    )
    
    db.execute('''
        INSERT OR REPLACE INTO user_states (user_id, state, updated_at)
        VALUES (?, 'creating_folder', ?)
    ''', (callback.from_user.id, int(time.time())))

# --- پیام همگانی ---

@Client.on_message(filters.regex("^📢 پیام همگانی$") & filters.private)
@admin_only
async def broadcast_start(client: Client, message: Message):
    """شروع پیام همگانی"""
    await message.reply_text(
        "📢 **پیام همگانی**\n\n"
        "پیام خود را ارسال کنید:\n"
        "(می‌تواند متن، عکس، ویدیو یا فایل باشد)"
    )
    
    db.execute('''
        INSERT OR REPLACE INTO user_states (user_id, state, updated_at)
        VALUES (?, 'broadcast_message', ?)
    ''', (message.from_user.id, int(time.time())))

@Client.on_message(filters.private)
async def handle_broadcast_message(client: Client, message: Message):
    """دریافت پیام برای ارسال"""
    user_id = message.from_user.id
    
    if user_id not in config.ADMIN_IDS:
        return
    
    state = db.fetchone('SELECT * FROM user_states WHERE user_id = ?', (user_id,))
    
    if not state or state['state'] != 'broadcast_message':
        return
    
    # ذخیره پیام
    db.execute('''
        UPDATE user_states SET data = ? WHERE user_id = ?
    ''', (str(message.id), user_id))
    
    await message.reply_text(
        "✅ **پیام دریافت شد**\n\n"
        "آیا مطمئن هستید که می‌خواهید این پیام را به همه کاربران ارسال کنید؟",
        reply_markup=broadcast_confirm()
    )

@Client.on_callback_query(filters.regex(r"^broadcast_confirm$"))
@admin_only
async def confirm_broadcast(client: Client, callback: CallbackQuery):
    """تأیید و ارسال پیام همگانی"""
    user_id = callback.from_user.id
    state = db.fetchone('SELECT * FROM user_states WHERE user_id = ?', (user_id,))
    
    message_id = int(state['data'])
    
    users = db.fetchall('SELECT user_id FROM users WHERE is_blocked = 0')
    
    success = 0
    failed = 0
    
    status_msg = await callback.message.edit_text(
        f"📤 **در حال ارسال...**\n\n"
        f"✅ موفق: {success}\n"
        f"❌ ناموفق: {failed}\n"
        f"📊 کل: {len(users)}"
    )
    
    for user in users:
        try:
            await client.copy_message(
                user['user_id'],
                callback.from_user.id,
                message_id
            )
            success += 1
        except:
            failed += 1
        
        # به‌روزرسانی هر ۱۰۰ کاربر
        if (success + failed) % 100 == 0:
            await status_msg.edit_text(
                f"📤 **در حال ارسال...**\n\n"
                f"✅ موفق: {success}\n"
                f"❌ ناموفق: {failed}\n"
                f"📊 کل: {len(users)}"
            )
    
    db.execute('DELETE FROM user_states WHERE user_id = ?', (user_id,))
    
    await status_msg.edit_text(
        f"✅ **ارسال به پایان رسید!**\n\n"
        f"✅ موفق: {success}\n"
        f"❌ ناموفق: {failed}\n"
        f"📊 کل: {len(users)}"
    )

# --- بکاپ ---

@Client.on_message(filters.regex("^💾 بکاپ$") & filters.private)
@admin_only
async def create_backup(client: Client, message: Message):
    """ساخت فایل بکاپ"""
    import shutil
    
    try:
        # کپی دیتابیس
        backup_file = f"backup_{int(time.time())}.db"
        shutil.copy2('database/bot.db', backup_file)
        
        # ارسال فایل
        await message.reply_document(
            backup_file,
            caption=f"💾 **فایل بکاپ**\n\n📅 {time.strftime('%Y/%m/%d %H:%M')}"
        )
        
        # حذف فایل موقت
        import os
        os.remove(backup_file)
        
    except Exception as e:
        await message.reply_text(f"❌ خطا در ساخت بکاپ: {e}")
