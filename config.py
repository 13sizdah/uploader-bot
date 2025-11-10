"""تنظیمات ربات"""

import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Config:
    """کلاس تنظیمات"""
    
    # اطلاعات ربات
    API_ID: int = int(os.getenv("API_ID", "0"))
    API_HASH: str = os.getenv("API_HASH", "")
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    
    # ادمین‌ها
    ADMIN_IDS: List[int] = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x]
    
    # دیتابیس
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "database/bot.db")
    
    # کانال‌ها
    STORAGE_CHANNEL: int = int(os.getenv("STORAGE_CHANNEL", "0"))
    BACKUP_CHANNEL: int = int(os.getenv("BACKUP_CHANNEL", "0"))
    LOG_CHANNEL: int = int(os.getenv("LOG_CHANNEL", "0"))
    
    # محدودیت‌ها
    FREE_DOWNLOAD_LIMIT: int = int(os.getenv("FREE_DOWNLOAD_LIMIT", "3"))
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "2097152000"))  # 2GB
    SPAM_TIMEOUT: int = int(os.getenv("SPAM_TIMEOUT", "3"))  # ثانیه
    
    # درگاه‌های پرداخت
    # زرین‌پال
    ZARINPAL_ENABLED: bool = os.getenv("ZARINPAL_ENABLED", "false").lower() == "true"
    ZARINPAL_MERCHANT: str = os.getenv("ZARINPAL_MERCHANT", "")
    ZARINPAL_SANDBOX: bool = os.getenv("ZARINPAL_SANDBOX", "false").lower() == "true"
    
    # زیبال
    ZIBAL_ENABLED: bool = os.getenv("ZIBAL_ENABLED", "false").lower() == "true"
    ZIBAL_MERCHANT: str = os.getenv("ZIBAL_MERCHANT", "")
    
    # نکست‌پی
    NEXTPAY_ENABLED: bool = os.getenv("NEXTPAY_ENABLED", "false").lower() == "true"
    NEXTPAY_API_KEY: str = os.getenv("NEXTPAY_API_KEY", "")
    
    # ترون
    TRON_ENABLED: bool = os.getenv("TRON_ENABLED", "false").lower() == "true"
    TRON_WALLET: str = os.getenv("TRON_WALLET", "")
    TRON_RATE: int = int(os.getenv("TRON_RATE", "55000"))  # USDT به تومان
    
    # تون
    TON_ENABLED: bool = os.getenv("TON_ENABLED", "false").lower() == "true"
    TON_WALLET: str = os.getenv("TON_WALLET", "")
    TON_RATE: int = int(os.getenv("TON_RATE", "280000"))  # TON به تومان
    
    # کارت به کارت
    CARD_ENABLED: bool = os.getenv("CARD_ENABLED", "false").lower() == "true"
    CARD_NUMBER: str = os.getenv("CARD_NUMBER", "")
    CARD_HOLDER: str = os.getenv("CARD_HOLDER", "")
    
    # وب‌هوک
    WEBHOOK_URL: str = os.getenv("WEBHOOK_URL", "")
    
    # ویژگی‌ها
    WATERMARK_ENABLED: bool = os.getenv("WATERMARK_ENABLED", "false").lower() == "true"
    WATERMARK_TEXT: str = os.getenv("WATERMARK_TEXT", "@YourBot")
    FORCE_JOIN: bool = os.getenv("FORCE_JOIN", "true").lower() == "true"
    
    # متن‌ها
    START_MESSAGE: str = """
🎉 **خوش آمدید!**

به ربات آپلودر پیشرفته خوش آمدید
برای استفاده از امکانات ربات، از منوی زیر استفاده کنید

🔹 دانلود رایگان: {free_downloads} بار در روز
💎 اشتراک ویژه: دانلود نامحدود
    """
    
    HELP_MESSAGE: str = """
📚 **راهنمای استفاده**

🔍 **جستجوی رسانه:**
- از دکمه جستجو یا اینلاین استفاده کنید
- کد رسانه را وارد کنید

💎 **خرید اشتراک:**
- از منوی اشتراک ویژه استفاده کنید
- روش پرداخت را انتخاب کنید

📊 **آمار:**
- مشاهده آمار دانلودها و اشتراک

❓ **سوالات بیشتر:**
- با پشتیبانی تماس بگیرید
    """

# نمونه سراسری
config = Config()

# بررسی تنظیمات ضروری
if not config.API_ID or not config.API_HASH or not config.BOT_TOKEN:
    raise ValueError("❌ لطفاً API_ID, API_HASH و BOT_TOKEN را در .env تنظیم کنید")

if not config.ADMIN_IDS:
    raise ValueError("❌ لطفاً حداقل یک ADMIN_ID تنظیم کنید")
