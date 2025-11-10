"""فایل اصلی ربات تلگرام"""

from pyrogram import Client
from pyrogram.enums import ParseMode
from config import config
from database.db import db
import time

# ایجاد کلاینت ربات
app = Client(
    "uploader_bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    parse_mode=ParseMode.MARKDOWN,
    workers=config.get('WORKERS', 4),
    plugins=dict(root="handlers")
)

# متغیر زمان شروع ربات
START_TIME = int(time.time())

@app.on_message()
async def log_messages(client, message):
    """لاگ پیام‌ها (اختیاری)"""
    if config.get('DEBUG_MODE', False):
        print(f"[{message.from_user.id}] {message.text}")

async def startup():
    """اجرای توابع هنگام استارت ربات"""
    print("🚀 ربات در حال راه‌اندازی...")
    
    # ایجاد جداول دیتابیس
    db.create_tables()
    print("✅ دیتابیس آماده شد")
    
    # بررسی تنظیمات
    if not config.API_ID or not config.BOT_TOKEN:
        print("❌ خطا: API_ID یا BOT_TOKEN تنظیم نشده است!")
        return False
    
    print(f"✅ ربات با موفقیت راه‌اندازی شد")
    print(f"📊 تعداد ادمین‌ها: {len(config.ADMIN_IDS)}")
    print(f"💳 درگاه‌های فعال: {sum([config.ZARINPAL_ENABLED, config.ZIBAL_ENABLED, config.NEXTPAY_ENABLED, config.TRON_ENABLED, config.TON_ENABLED, config.CARD_ENABLED])}")
    
    return True

async def shutdown():
    """اجرای توابع هنگام خاموش شدن ربات"""
    print("🔴 ربات در حال خاموش شدن...")
    
    # بستن اتصال دیتابیس
    db.close()
    print("✅ اتصالات بسته شد")

if __name__ == "__main__":
    try:
        # استارت ربات
        if startup():
            print("="*50)
            print("🤖 ربات آپلودر پیشرفته - نسخه 4.5")
            print("="*50)
            app.run()
    except KeyboardInterrupt:
        print("\n⚠️ ربات توسط کاربر متوقف شد")
    except Exception as e:
        print(f"❌ خطای حیاتی: {e}")
    finally:
        shutdown()
