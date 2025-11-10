"""کیبوردهای کاربران"""

from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)

def main_menu():
    """منوی اصلی"""
    return ReplyKeyboardMarkup([
        [KeyboardButton("🔍 جستجوی رسانه"), KeyboardButton("📊 آمار من")],
        [KeyboardButton("💎 اشتراک ویژه"), KeyboardButton("📚 راهنما")],
        [KeyboardButton("☎️ پشتیبانی"), KeyboardButton("ℹ️ درباره ربات")]
    ], resize_keyboard=True)

def subscription_plans(plans: list):
    """لیست پلن‌های اشتراک"""
    keyboard = []
    
    for plan in plans:
        keyboard.append([
            InlineKeyboardButton(
                f"💎 {plan['name']} - {plan['price']:,} تومان",
                callback_data=f"buy_sub:{plan['id']}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")])
    
    return InlineKeyboardMarkup(keyboard)

def payment_methods():
    """روش‌های پرداخت"""
    from config import config
    
    keyboard = []
    
    if config.ZARINPAL_ENABLED:
        keyboard.append([InlineKeyboardButton("💳 زرین‌پال", callback_data="pay:zarinpal")])
    
    if config.ZIBAL_ENABLED:
        keyboard.append([InlineKeyboardButton("💳 زیبال", callback_data="pay:zibal")])
    
    if config.NEXTPAY_ENABLED:
        keyboard.append([InlineKeyboardButton("💳 نکست‌پی", callback_data="pay:nextpay")])
    
    if config.TRON_ENABLED:
        keyboard.append([InlineKeyboardButton("🪙 ترون (USDT)", callback_data="pay:tron")])
    
    if config.TON_ENABLED:
        keyboard.append([InlineKeyboardButton("🪙 تون (TON)", callback_data="pay:ton")])
    
    if config.CARD_ENABLED:
        keyboard.append([InlineKeyboardButton("💵 کارت به کارت", callback_data="pay:card")])
    
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_plans")])
    
    return InlineKeyboardMarkup(keyboard)

def media_actions(media_code: str, has_password: bool = False):
    """اکشن‌های رسانه"""
    keyboard = [
        [InlineKeyboardButton("⬇️ دانلود", callback_data=f"download:{media_code}")],
        [
            InlineKeyboardButton("👍", callback_data=f"like:{media_code}"),
            InlineKeyboardButton("👎", callback_data=f"dislike:{media_code}")
        ],
        [InlineKeyboardButton("💬 کامنت", callback_data=f"comment:{media_code}")],
        [InlineKeyboardButton("📤 اشتراک‌گذاری", callback_data=f"share:{media_code}")]
    ]
    
    if has_password:
        keyboard.insert(0, [InlineKeyboardButton("🔓 ورود رمز عبور", callback_data=f"pass:{media_code}")])
    
    return InlineKeyboardMarkup(keyboard)

def confirm_payment(transaction_id: int):
    """تأیید پرداخت (برای کارت به کارت)"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ پرداخت انجام شد", callback_data=f"confirm_payment:{transaction_id}")],
        [InlineKeyboardButton("❌ انصراف", callback_data="cancel_payment")]
    ])

def back_button(callback: str = "back_to_main"):
    """دکمه بازگشت"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 بازگشت", callback_data=callback)]
    ])
