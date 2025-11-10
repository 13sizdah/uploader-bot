"""هندلر مدیریت رسانه‌ها"""

from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from database.db import db
from utils.decorators import admin_only, anti_spam
from utils.helpers import generate_code, format_size, format_number
from keyboards.admin import media_management, media_security_options
from keyboards.user import media_actions
import time

# --- افزودن رسانه ---

@Client.on_message(filters.regex("^📤 افزودن رسانه$") & filters.private)
@admin_only
async def add_media_start(client: Client, message: Message):
    """شروع افزودن رسانه"""
    await message.reply_text(
        "📤 **افزودن رسانه جدید**\n\n"
        "لطفاً فایل، عکس یا ویدیوی خود را ارسال کنید"
    )
    
    # ذخیره state
    db.execute('''
        INSERT OR REPLACE INTO user_states (user_id, state, updated_at)
        VALUES (?, 'awaiting_media', ?)
    ''', (message.from_user.id, int(time.time())))

@Client.on_message(
    (filters.document | filters.photo | filters.video | filters.audio) & 
    filters.private
)
async def receive_media(client: Client, message: Message):
    """دریافت رسانه"""
    user_id = message.from_user.id
    
    # بررسی state
    state = db.fetchone('SELECT * FROM user_states WHERE user_id = ?', (user_id,))
    
    if not state or state['state'] != 'awaiting_media':
        return
    
    if user_id not in config.ADMIN_IDS:
        return
    
    # تشخیص نوع رسانه
    if message.document:
        media_type = "document"
        file_id = message.document.file_id
        file_size = message.document.file_size
        title = message.document.file_name
        duration = 0
    elif message.video:
        media_type = "video"
        file_id = message.video.file_id
        file_size = message.video.file_size
        title = message.video.file_name or "ویدیو"
        duration = message.video.duration
    elif message.audio:
        media_type = "audio"
        file_id = message.audio.file_id
        file_size = message.audio.file_size
        title = message.audio.title or message.audio.file_name or "صوت"
        duration = message.audio.duration
    else:  # photo
        media_type = "photo"
        file_id = message.photo.file_id
        file_size = message.photo.file_size
        title = "عکس"
        duration = 0
    
    # آپلود به کانال ذخیره‌سازی
    try:
        storage_msg = await message.copy(config.STORAGE_CHANNEL)
        storage_file_id = storage_msg.id
    except Exception as e:
        await message.reply_text(f"❌ خطا در آپلود: {e}")
        return
    
    # تولید کد یکتا
    media_code = generate_code()
    
    # ذخیره در دیتابیس
    media_id = db.execute('''
        INSERT INTO media (
            media_code, file_id, media_type, title, file_size, duration, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        media_code,
        file_id,
        media_type,
        title,
        file_size,
        duration,
        int(time.time()),
        int(time.time())
    ))
    
    # پاک کردن state
    db.execute('DELETE FROM user_states WHERE user_id = ?', (user_id,))
    
    # نمایش اطلاعات
    text = f"""
✅ **رسانه با موفقیت افزوده شد!**

🆔 کد: `{media_code}`
📁 نوع: {media_type}
📝 نام: {title}
💾 حجم: {format_size(file_size)}
    """
    
    if duration > 0:
        text += f"\n⏱ مدت: {duration} ثانیه"
    
    await message.reply_text(text, reply_markup=media_management())

# --- جستجوی رسانه ---

@Client.on_message(filters.regex("^🔍 جستجوی رسانه$") & filters.private)
async def search_media(client: Client, message: Message):
    """جستجوی رسانه"""
    await message.reply_text(
        "🔍 **جستجوی رسانه**\n\n"
        "کد رسانه را وارد کنید:"
    )
    
    db.execute('''
        INSERT OR REPLACE INTO user_states (user_id, state, updated_at)
        VALUES (?, 'searching_media', ?)
    ''', (message.from_user.id, int(time.time())))

@Client.on_message(filters.text & filters.private)
async def handle_search(client: Client, message: Message):
    """پردازش جستجو"""
    user_id = message.from_user.id
    
    state = db.fetchone('SELECT * FROM user_states WHERE user_id = ?', (user_id,))
    
    if not state or state['state'] != 'searching_media':
        return
    
    media_code = message.text.strip().upper()
    
    # جستجو در دیتابیس
    media = db.fetchone('SELECT * FROM media WHERE media_code = ? AND is_active = 1', (media_code,))
    
    if not media:
        await message.reply_text("❌ رسانه‌ای با این کد یافت نشد!")
        return
    
    # پاک کردن state
    db.execute('DELETE FROM user_states WHERE user_id = ?', (user_id,))
    
    # نمایش رسانه
    await show_media(client, message, media)

async def show_media(client: Client, message: Message, media: dict):
    """نمایش رسانه"""
    from utils.helpers import is_premium, can_download_free
    
    user_id = message.from_user.id
    
    # به‌روزرسانی بازدید
    total_views = media['fake_views'] + media['real_views'] + 1
    db.execute('''
        UPDATE media SET real_views = real_views + 1
        WHERE id = ?
    ''', (media['id'],))
    
    # ساخت کپشن
    caption = f"""
📁 **{media['title']}**

"""
    
    if media['description']:
        caption += f"{media['description']}\n\n"
    
    caption += f"""
🆔 کد: `{media['media_code']}`
💾 حجم: {format_size(media['file_size'])}
👁 بازدید: {format_number(total_views)}
⬇️ دانلود: {format_number(media['fake_downloads'] + media['real_downloads'])}
👍 لایک: {format_number(media['fake_likes'] + media['real_likes'])}
    """
    
    # بررسی دسترسی
    can_access = False
    
    if is_premium(user_id):
        can_access = True
    elif can_download_free(user_id):
        can_access = True
    
    # بررسی محدودیت دانلود
    if media['download_limit'] > 0 and media['current_downloads'] >= media['download_limit']:
        caption += "\n\n⚠️ محدودیت دانلود به پایان رسیده است"
        can_access = False
    
    # بررسی انقضا
    if media['expire_time'] > 0 and media['expire_time'] < int(time.time()):
        caption += "\n\n⚠️ این رسانه منقضی شده است"
        can_access = False
    
    # امضا
    if media['watermark_text']:
        caption += f"\n\n{media['watermark_text']}"
    
    keyboard = media_actions(media['media_code'], bool(media['password']))
    
    # ارسال رسانه
    try:
        if media['media_type'] == 'photo':
            await message.reply_photo(
                media['file_id'],
                caption=caption,
                reply_markup=keyboard
            )
        elif media['media_type'] == 'video':
            await message.reply_video(
                media['file_id'],
                caption=caption,
                reply_markup=keyboard
            )
        elif media['media_type'] == 'audio':
            await message.reply_audio(
                media['file_id'],
                caption=caption,
                reply_markup=keyboard
            )
        else:
            await message.reply_document(
                media['file_id'],
                caption=caption,
                reply_markup=keyboard
            )
    except Exception as e:
        await message.reply_text(f"❌ خطا در نمایش رسانه: {e}")

# --- دانلود رسانه ---

@Client.on_callback_query(filters.regex(r"^download:"))
@anti_spam(3)
async def download_media(client: Client, callback: CallbackQuery):
    """دانلود رسانه"""
    from utils.helpers import is_premium, can_download_free, increment_download
    
    user_id = callback.from_user.id
    media_code = callback.data.split(":")[1]
    
    media = db.fetchone('SELECT * FROM media WHERE media_code = ?', (media_code,))
    
    if not media:
        await callback.answer("❌ رسانه یافت نشد!", show_alert=True)
        return
    
    # بررسی رمز عبور
    if media['password']:
        await callback.answer("🔐 ابتدا رمز عبور را وارد کنید", show_alert=True)
        return
    
    # بررسی دسترسی
    if not is_premium(user_id) and not can_download_free(user_id):
        await callback.answer("❌ سهمیه دانلود رایگان شما تمام شده است!", show_alert=True)
        return
    
    # ارسال فایل
    try:
        await callback.message.reply_document(
            media['file_id'],
            caption=f"✅ دانلود موفق\n\n🆔 کد: `{media_code}`"
        )
        
        # به‌روزرسانی آمار
        db.execute('''
            UPDATE media 
            SET real_downloads = real_downloads + 1,
                current_downloads = current_downloads + 1
            WHERE id = ?
        ''', (media['id'],))
        
        # ثبت لاگ
        db.execute('''
            INSERT INTO downloads (user_id, media_id, downloaded_at)
            VALUES (?, ?, ?)
        ''', (user_id, media['id'], int(time.time())))
        
        increment_download(user_id)
        
        await callback.answer("✅ دانلود با موفقیت انجام شد")
        
    except Exception as e:
        await callback.answer(f"❌ خطا: {e}", show_alert=True)
