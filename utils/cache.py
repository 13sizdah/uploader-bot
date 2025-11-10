"""سیستم کشینگ با TTL"""

import time
from typing import Any, Optional, Dict
import threading

class TTLCache:
    """کش با زمان انقضا"""
    
    def __init__(self, ttl: int = 300):
        """
        ttl: زمان انقضا به ثانیه (پیش‌فرض 5 دقیقه)
        """
        self.cache: Dict[str, tuple[Any, float]] = {}
        self.ttl = ttl
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """دریافت از کش"""
        with self.lock:
            if key in self.cache:
                value, expire_time = self.cache[key]
                if time.time() < expire_time:
                    return value
                else:
                    del self.cache[key]
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """ذخیره در کش"""
        with self.lock:
            expire_time = time.time() + (ttl or self.ttl)
            self.cache[key] = (value, expire_time)
    
    def delete(self, key: str):
        """حذف از کش"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
    
    def clear(self):
        """پاکسازی کل کش"""
        with self.lock:
            self.cache.clear()
    
    def cleanup(self):
        """پاکسازی آیتم‌های منقضی شده"""
        with self.lock:
            current_time = time.time()
            expired_keys = [
                k for k, (_, exp) in self.cache.items()
                if current_time >= exp
            ]
            for key in expired_keys:
                del self.cache[key]

# نمونه‌های کش برای بخش‌های مختلف
user_cache = TTLCache(ttl=300)  # 5 دقیقه
media_cache = TTLCache(ttl=600)  # 10 دقیقه
channel_cache = TTLCache(ttl=3600)  # 1 ساعت
