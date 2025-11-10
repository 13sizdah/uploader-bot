"""دکوریتورهای سفارشی"""

from functools import wraps
from pyrogram.types import Message, CallbackQuery
from config import config
from database.db import db
import time

def admin_only(func):
    """محدودیت دسترسی به ادمین‌ها"""
    @wraps(func)
    async def wrapper(client, update):
        user_id = update.from_user.id
        
        if user_id not in config.ADMIN_IDS:
            if isinstance(update, CallbackQuery):
                await update.answer("⛔️ شما به این بخش دسترسی ندارید!", show_alert=True)
            else:
                await update.reply_text("⛔️ این بخش فقط برای ادمین‌ها است!")
            return
        
        return await func(client, update)
    
    return wrapper

def premium_only(func):
    """محدودیت به کاربران پرمیوم"""
    @wraps(func)
    async def wrapper(client, update):
        user_id = update.from_user.id
        
        from utils.helpers import is_premium
        
        if not is_premium(user_id):
            text = "💎 این امکان ویژه کاربران پرمیوم است!\n\nبرای خرید اشتراک از منوی زیر استفاده کنید"
            
            if isinstance(update, CallbackQuery):
                await update.answer("💎 فقط برای اعضای ویژه!", show_alert=True)
            else:
                await update.reply_text(text)
            return
        
        return await func(client, update)
    
    return wrapper

def anti_spam(seconds: int = 3):
    """جلوگیری از اسپم"""
    def decorator(func):
        @wraps(func)
        async def wrapper(client, update):
            user_id = update.from_user.id
            
            # بررسی آخرین فعالیت
            last_activity = db.fetchone(
                'SELECT last_activity FROM users WHERE user_id = ?',
                (user_id,)
            )
            
            current_time = int(time.time())
            
            if last_activity and (current_time - last_activity['last_activity']) < seconds:
                if isinstance(update, CallbackQuery):
                    await update.answer(
                        f"⏳ لطفاً {seconds} ثانیه صبر کنید",
                        show_alert=True
                    )
                return
            
            # به‌روزرسانی زمان
            db.execute(
                'UPDATE users SET last_activity = ? WHERE user_id = ?',
                (current_time, user_id)
            )
            
            return await func(client, update)
        
        return wrapper
    return decorator
