"""توابع کمکی"""

import time
import random
import string
from database.db import db
from config import config

def format_number(num: int) -> str:
    """فرمت اعداد با کاما"""
    return f"{num:,}"

def format_size(bytes_size: int) -> str:
    """تبدیل بایت به فرمت خوانا"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"

def format_duration(seconds: int) -> str:
    """تبدیل ثانیه به فرمت خوانا"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"

def generate_transaction_id() -> str:
    """تولید شناسه تراکنش یکتا"""
    timestamp = str(int(time.time()))[-6:]
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"TRX{timestamp}{random_str}"

def generate_media_code() -> str:
    """تولید کد رسانه یکتا"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=8))

async def check_force_channels(client, user_id: int) -> tuple[bool, list]:
    """بررسی عضویت در کانال‌های اجباری"""
    channels = db.fetchall('SELECT * FROM force_channels WHERE is_active = 1')
    
    if not channels:
        return True, []
    
    not_joined = []
    
    for channel in channels:
        try:
            member = await client.get_chat_member(channel['channel_id'], user_id)
            if member.status in ['left', 'kicked']:
                not_joined.append(channel)
        except:
            not_joined.append(channel)
    
    return len(not_joined) == 0, not_joined

def check_subscription_status(user_id: int) -> tuple[bool, int]:
    """بررسی وضعیت اشتراک کاربر"""
    user = db.fetchone('SELECT * FROM users WHERE user_id = ?', (user_id,))
    
    if not user or not user['is_premium']:
        return False, 0
    
    now = int(time.time())
    if user['subscription_end'] > now:
        days_left = (user['subscription_end'] - now) // 86400
        return True, days_left
    else:
        # اشتراک منقضی شده
        db.execute('UPDATE users SET is_premium = 0 WHERE user_id = ?', (user_id,))
        return False, 0

def calculate_fake_stats(real_value: int, multiplier: float = 1.5) -> int:
    """محاسبه آمار فیک"""
    fake_value = int(real_value * multiplier)
    # اضافه کردن تصادفی برای واقعی‌تر شدن
    variance = random.randint(-int(fake_value * 0.1), int(fake_value * 0.1))
    return max(0, fake_value + variance)

def is_admin(user_id: int) -> bool:
    """بررسی ادمین بودن کاربر"""
    return user_id in config.ADMIN_IDS

def get_media_type_emoji(media_type: str) -> str:
    """دریافت ایموجی نوع رسانه"""
    emojis = {
        'photo': '🖼',
        'video': '🎥',
        'document': '📄',
        'audio': '🎵',
        'animation': '🎬',
        'voice': '🎤'
    }
    return emojis.get(media_type, '📁')

def parse_time_string(time_str: str) -> int:
    """تبدیل رشته زمان به ثانیه (مثال: "5m", "2h", "1d")"""
    units = {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400,
        'w': 604800
    }
    
    if time_str[-1] in units:
        return int(time_str[:-1]) * units[time_str[-1]]
    return int(time_str)

def get_bot_uptime(start_time: int) -> str:
    """محاسبه مدت زمان آنلاین بودن ربات"""
    uptime = int(time.time()) - start_time
    days = uptime // 86400
    hours = (uptime % 86400) // 3600
    minutes = (uptime % 3600) // 60
    
    return f"{days}d {hours}h {minutes}m"

def validate_card_number(card_number: str) -> bool:
    """اعتبارسنجی شماره کارت بانکی"""
    card_number = card_number.replace('-', '').replace(' ', '')
    
    if len(card_number) != 16 or not card_number.isdigit():
        return False
    
    # الگوریتم Luhn
    digits = [int(d) for d in card_number]
    checksum = 0
    
    for i in range(len(digits) - 2, -1, -2):
        digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9
    
    return sum(digits) % 10 == 0

def escape_markdown(text: str) -> str:
    """Escape کاراکترهای ویژه Markdown"""
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text
