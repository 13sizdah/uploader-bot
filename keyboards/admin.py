"""کیبوردهای پنل ادمین"""

from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)

def admin_panel():
    """پنل اصلی ادمین"""
    return ReplyKeyboardMarkup([
        [KeyboardButton("📤 افزودن رسانه"), KeyboardButton("🔍 جستجوی رسانه")],
        [KeyboardButton("📁 مدیریت پوشه‌ها"), KeyboardButton("👥 مدیریت کاربران")],
        [KeyboardButton("💎 مدیریت اشتراک‌ها"), KeyboardButton("💰 مدیریت پرداخت")],
        [KeyboardButton("📢 پیام همگانی"), KeyboardButton("📊 آمار کامل")],
        [KeyboardButton("⚙️ تنظیمات"), KeyboardButton("💾 بکاپ")],
        [KeyboardButton("🔙 بازگشت به منوی اصلی")]
    ], resize_keyboard=True)

def media_management():
    """مدیریت رسانه"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ ویرایش", callback_data="admin_edit_media")],
        [InlineKeyboardButton("🔐 تنظیمات امنیتی", callback_data="admin_media_security")],
        [InlineKeyboardButton("📊 آمار فیک", callback_data="admin_fake_stats")],
        [InlineKeyboardButton("🗑 حذف", callback_data="admin_delete_media")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_main")]
    ])

def media_security_options():
    """تنظیمات امنیتی رسانه"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔒 تنظیم رمز عبور", callback_data="set_password")],
        [InlineKeyboardButton("🔢 محدودیت دانلود", callback_data="set_limit")],
        [InlineKeyboardButton("⏰ زمان انقضا", callback_data="set_expire")],
        [InlineKeyboardButton("⏱ تایمر حذف", callback_data="set_delete_timer")],
        [InlineKeyboardButton("🔒 قفل فوروارد", callback_data="toggle_forward_lock")],
        [InlineKeyboardButton("💾 قفل ذخیره", callback_data="toggle_save_lock")],
        [InlineKeyboardButton("📢 قفل کانال", callback_data="set_channel_lock")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_media_menu")]
    ])

def folders_menu():
    """منوی پوشه‌ها"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ پوشه جدید", callback_data="admin_new_folder")],
        [InlineKeyboardButton("📂 لیست پوشه‌ها", callback_data="admin_list_folders")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_main")]
    ])

def folder_actions(folder_id: int):
    """اکشن‌های پوشه"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ ویرایش", callback_data=f"edit_folder:{folder_id}")],
        [InlineKeyboardButton("➕ زیرپوشه", callback_data=f"subfolder:{folder_id}")],
        [InlineKeyboardButton("🗑 حذف", callback_data=f"delete_folder:{folder_id}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_list_folders")]
    ])

def user_management(user_id: int):
    """مدیریت کاربر"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 اعطای اشتراک", callback_data=f"grant_sub:{user_id}")],
        [InlineKeyboardButton("🚫 بلاک/آنبلاک", callback_data=f"toggle_block:{user_id}")],
        [InlineKeyboardButton("📊 مشاهده آمار", callback_data=f"user_stats:{user_id}")],
        [InlineKeyboardButton("🗑 حذف", callback_data=f"delete_user:{user_id}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_main")]
    ])

def settings_menu():
    """منوی تنظیمات"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔓 قفل‌ها", callback_data="admin_locks")],
        [InlineKeyboardButton("✍️ امضا", callback_data="admin_signature")],
        [InlineKeyboardButton("📊 آمار فیک پیش‌فرض", callback_data="admin_default_fake")],
        [InlineKeyboardButton("🔌 وضعیت ربات", callback_data="admin_bot_status")],
        [InlineKeyboardButton("💳 درگاه‌های پرداخت", callback_data="admin_payment_gateways")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_main")]
    ])

def payment_gateways():
    """مدیریت درگاه‌های پرداخت"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 زرین‌پال", callback_data="gateway:zarinpal")],
        [InlineKeyboardButton("💳 زیبال", callback_data="gateway:zibal")],
        [InlineKeyboardButton("💳 نکست‌پی", callback_data="gateway:nextpay")],
        [InlineKeyboardButton("🪙 ترون", callback_data="gateway:tron")],
        [InlineKeyboardButton("🪙 تون", callback_data="gateway:ton")],
        [InlineKeyboardButton("💵 کارت به کارت", callback_data="gateway:card")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_settings")]
    ])

def toggle_button(name: str, is_enabled: bool, callback: str):
    """دکمه روشن/خاموش"""
    status = "✅ فعال" if is_enabled else "❌ غیرفعال"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{name}: {status}", callback_data=callback)],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_settings")]
    ])

def broadcast_confirm():
    """تأیید پیام همگانی"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ ارسال", callback_data="broadcast_confirm")],
        [InlineKeyboardButton("❌ انصراف", callback_data="broadcast_cancel")]
    ])

def search_type():
    """نوع جستجو"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔤 جستجو با کد", callback_data="search:code")],
        [InlineKeyboardButton("📝 جستجو با کپشن", callback_data="search:caption")],
        [InlineKeyboardButton("📁 جستجو با پوشه", callback_data="search:folder")],
        [InlineKeyboardButton("🎬 جستجو با نوع", callback_data="search:type")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_main")]
    ])

def delete_options():
    """گزینه‌های حذف"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🗑 حذف این مورد", callback_data="delete_single")],
        [InlineKeyboardButton("🗑 حذف دسته‌جمعی", callback_data="delete_bulk")],
        [InlineKeyboardButton("❌ انصراف", callback_data="admin_main")]
    ])
