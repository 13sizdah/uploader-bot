"""مدیریت دیتابیس بهینه شده"""

import sqlite3
import threading
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class Database:
    """کلاس مدیریت دیتابیس با الگوی Singleton"""
    
    _instance = None
    _lock = threading.Lock()
    _local = threading.local()
    
    def __new__(cls, db_path: str = "database/bot.db"):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.db_path = db_path
                    cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """راه‌اندازی اولیه"""
        import os
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # ایجاد اتصال اولیه و تنظیمات
        conn = self._get_connection()
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=-64000")  # 64MB
        conn.execute("PRAGMA temp_store=MEMORY")
        conn.execute("PRAGMA mmap_size=268435456")  # 256MB
        conn.commit()
        logger.info("✅ Database initialized with optimizations")
    
    def _get_connection(self) -> sqlite3.Connection:
        """دریافت اتصال thread-safe"""
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn
    
    def execute(self, query: str, params: tuple = ()) -> Optional[int]:
        """اجرای کوئری با بازگشت lastrowid"""
        conn = self._get_connection()
        try:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            conn.rollback()
            return None
    
    def fetchone(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """دریافت یک رکورد"""
        conn = self._get_connection()
        try:
            cursor = conn.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            return None
    
    def fetchall(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """دریافت همه رکوردها"""
        conn = self._get_connection()
        try:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            return []
    
    def create_tables(self):
        """ایجاد جداول"""
        
        # جدول کاربران
        self.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                is_premium INTEGER DEFAULT 0,
                subscription_end INTEGER DEFAULT 0,
                daily_downloads INTEGER DEFAULT 0,
                total_downloads INTEGER DEFAULT 0,
                is_blocked INTEGER DEFAULT 0,
                joined_at INTEGER,
                last_activity INTEGER,
                last_download INTEGER DEFAULT 0
            )
        ''')
        
        # جدول رسانه‌ها
        self.execute('''
            CREATE TABLE IF NOT EXISTS media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                media_code TEXT UNIQUE NOT NULL,
                file_id TEXT NOT NULL,
                media_type TEXT NOT NULL,
                title TEXT,
                description TEXT,
                folder_id INTEGER,
                file_size INTEGER DEFAULT 0,
                duration INTEGER DEFAULT 0,
                thumbnail_file_id TEXT,
                
                -- تنظیمات پیشرفته
                password TEXT,
                download_limit INTEGER DEFAULT 0,
                current_downloads INTEGER DEFAULT 0,
                expire_time INTEGER DEFAULT 0,
                delete_timer INTEGER DEFAULT 0,
                
                -- قفل‌ها
                lock_forward INTEGER DEFAULT 0,
                lock_save INTEGER DEFAULT 0,
                lock_channel TEXT,
                watermark_text TEXT,
                
                -- آمار فیک
                fake_views INTEGER DEFAULT 0,
                fake_downloads INTEGER DEFAULT 0,
                fake_likes INTEGER DEFAULT 0,
                
                -- آمار واقعی
                real_views INTEGER DEFAULT 0,
                real_downloads INTEGER DEFAULT 0,
                real_likes INTEGER DEFAULT 0,
                
                is_active INTEGER DEFAULT 1,
                created_at INTEGER,
                updated_at INTEGER
            )
        ''')
        
        # جدول پوشه‌ها
        self.execute('''
            CREATE TABLE IF NOT EXISTS folders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                parent_id INTEGER,
                description TEXT,
                is_active INTEGER DEFAULT 1,
                created_at INTEGER
            )
        ''')
        
        # جدول اشتراک‌ها
        self.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                duration_days INTEGER NOT NULL,
                price INTEGER NOT NULL,
                download_limit INTEGER DEFAULT -1,
                description TEXT,
                is_active INTEGER DEFAULT 1,
                created_at INTEGER
            )
        ''')
        
        # جدول تراکنش‌ها
        self.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                subscription_id INTEGER,
                amount INTEGER NOT NULL,
                payment_method TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                transaction_id TEXT,
                receipt_file_id TEXT,
                authority TEXT,
                ref_id TEXT,
                created_at INTEGER,
                completed_at INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (subscription_id) REFERENCES subscriptions(id)
            )
        ''')
        
        # جدول کانال‌های جوین اجباری
        self.execute('''
            CREATE TABLE IF NOT EXISTS force_channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id INTEGER NOT NULL,
                channel_username TEXT,
                channel_name TEXT,
                is_active INTEGER DEFAULT 1,
                created_at INTEGER
            )
        ''')
        
        # جدول تنظیمات
        self.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at INTEGER
            )
        ''')
        
        # جدول لاگ دانلود
        self.execute('''
            CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                media_id INTEGER NOT NULL,
                downloaded_at INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (media_id) REFERENCES media(id)
            )
        ''')
        
        # جدول لاگ بکاپ
        self.execute('''
            CREATE TABLE IF NOT EXISTS backup_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id TEXT NOT NULL,
                file_size INTEGER,
                created_at INTEGER
            )
        ''')
        
        # جدول تبلیغات
        self.execute('''
            CREATE TABLE IF NOT EXISTS ads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id TEXT NOT NULL,
                ad_type TEXT NOT NULL,
                show_every INTEGER DEFAULT 5,
                is_active INTEGER DEFAULT 1,
                views_count INTEGER DEFAULT 0,
                created_at INTEGER
            )
        ''')
        
        # جدول ری‌اکشن‌ها
        self.execute('''
            CREATE TABLE IF NOT EXISTS reactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                media_id INTEGER NOT NULL,
                reaction_type TEXT NOT NULL,
                created_at INTEGER,
                UNIQUE(user_id, media_id, reaction_type)
            )
        ''')
        
        # جدول کامنت‌ها
        self.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                media_id INTEGER NOT NULL,
                comment_text TEXT NOT NULL,
                is_approved INTEGER DEFAULT 0,
                created_at INTEGER
            )
        ''')
        
        # جدول state کاربران (برای مدیریت مراحل)
        self.execute('''
            CREATE TABLE IF NOT EXISTS user_states (
                user_id INTEGER PRIMARY KEY,
                state TEXT NOT NULL,
                data TEXT,
                updated_at INTEGER
            )
        ''')
        
        # ایجاد ایندکس‌ها
        self._create_indexes()
        
        logger.info("✅ All tables created successfully")
    
    def _create_indexes(self):
        """ایجاد ایندکس‌های بهینه"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_media_code ON media(media_code)",
            "CREATE INDEX IF NOT EXISTS idx_media_folder ON media(folder_id)",
            "CREATE INDEX IF NOT EXISTS idx_media_active ON media(is_active)",
            "CREATE INDEX IF NOT EXISTS idx_users_premium ON users(is_premium)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status)",
            "CREATE INDEX IF NOT EXISTS idx_downloads_user ON downloads(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_downloads_media ON downloads(media_id)",
            "CREATE INDEX IF NOT EXISTS idx_reactions_media ON reactions(media_id)",
        ]
        
        for index in indexes:
            self.execute(index)
        
        logger.info("✅ Indexes created successfully")

# نمونه سراسری
db = Database()
