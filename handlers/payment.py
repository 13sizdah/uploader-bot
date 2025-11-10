"""هندلر پرداخت‌ها و درگاه‌ها"""

from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from database.db import db
from keyboards.user import payment_methods, confirm_payment, subscription_plans
from utils.helpers import generate_transaction_id
from config import config
import time
import aiohttp
import json

# --- نمایش پلن‌های اشتراک ---

@Client.on_message(filters.regex("^💎 اشتراک ویژه$") & filters.private)
async def show_subscription_plans(client: Client, message: Message):
    """نمایش پلن‌های اشتراک"""
    plans = [
        {"id": 1, "name": "۱ ماهه", "price": 50000, "days": 30},
        {"id": 2, "name": "۳ ماهه", "price": 120000, "days": 90},
        {"id": 3, "name": "۶ ماهه", "price": 200000, "days": 180},
        {"id": 4, "name": "۱ ساله", "price": 350000, "days": 365}
    ]
    
    text = """
💎 **پلن‌های اشتراک ویژه**

✨ **مزایای اشتراک:**
• دانلود نامحدود
• دسترسی به رسانه‌های VIP
• پشتیبانی اختصاصی
• بدون تبلیغات
• اولویت در دانلود

📋 **پلن مورد نظر خود را انتخاب کنید:**
    """
    
    await message.reply_text(text, reply_markup=subscription_plans(plans))

# --- انتخاب روش پرداخت ---

@Client.on_callback_query(filters.regex(r"^buy_sub:"))
async def select_payment_method(client: Client, callback: CallbackQuery):
    """انتخاب روش پرداخت"""
    plan_id = int(callback.data.split(":")[1])
    
    plans = {
        1: {"name": "۱ ماهه", "price": 50000, "days": 30},
        2: {"name": "۳ ماهه", "price": 120000, "days": 90},
        3: {"name": "۶ ماهه", "price": 200000, "days": 180},
        4: {"name": "۱ ساله", "price": 350000, "days": 365}
    }
    
    plan = plans.get(plan_id)
    if not plan:
        await callback.answer("❌ پلن نامعتبر!", show_alert=True)
        return
    
    # ذخیره انتخاب در state
    db.execute('''
        INSERT OR REPLACE INTO user_states (user_id, state, data, updated_at)
        VALUES (?, 'selecting_payment', ?, ?)
    ''', (callback.from_user.id, json.dumps(plan), int(time.time())))
    
    text = f"""
💎 **پلن انتخابی:** {plan['name']}
💰 **مبلغ:** {plan['price']:,} تومان
⏳ **مدت:** {plan['days']} روز

🔹 **روش پرداخت را انتخاب کنید:**
    """
    
    await callback.message.edit_text(text, reply_markup=payment_methods())
    await callback.answer()

# --- 💳 زرین‌پال ---

@Client.on_callback_query(filters.regex(r"^pay:zarinpal$"))
async def zarinpal_payment(client: Client, callback: CallbackQuery):
    """پرداخت با زرین‌پال"""
    if not config.ZARINPAL_ENABLED:
        await callback.answer("❌ این روش غیرفعال است", show_alert=True)
        return
    
    user_id = callback.from_user.id
    state = db.fetchone('SELECT * FROM user_states WHERE user_id = ?', (user_id,))
    
    if not state or state['state'] != 'selecting_payment':
        await callback.answer("❌ خطای نامشخص!", show_alert=True)
        return
    
    plan = json.loads(state['data'])
    amount = plan['price']
    
    # ساخت تراکنش
    transaction_id = generate_transaction_id()
    
    db.execute('''
        INSERT INTO transactions (
            transaction_id, user_id, amount, payment_method, 
            plan_days, status, created_at
        ) VALUES (?, ?, ?, 'zarinpal', ?, 'pending', ?)
    ''', (transaction_id, user_id, amount, plan['days'], int(time.time())))
    
    # درخواست پرداخت از زرین‌پال
    try:
        url = "https://api.zarinpal.com/pg/v4/payment/request.json"
        data = {
            "merchant_id": config.ZARINPAL_MERCHANT,
            "amount": amount * 10,  # ریال
            "description": f"خرید اشتراک {plan['name']}",
            "callback_url": f"{config.WEBHOOK_URL}/verify/zarinpal/{transaction_id}",
            "metadata": {"mobile": "", "email": ""}
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                result = await response.json()
        
        if result['data']['code'] == 100:
            authority = result['data']['authority']
            payment_url = f"https://www.zarinpal.com/pg/StartPay/{authority}"
            
            # ذخیره authority
            db.execute('''
                UPDATE transactions SET payment_data = ? WHERE transaction_id = ?
            ''', (authority, transaction_id))
            
            await callback.message.edit_text(
                f"✅ **لینک پرداخت ساخته شد**\n\n"
                f"💰 مبلغ: {amount:,} تومان\n"
                f"🆔 شناسه تراکنش: `{transaction_id}`\n\n"
                f"🔗 [پرداخت کنید]({payment_url})",
                disable_web_page_preview=True
            )
        else:
            await callback.answer("❌ خطا در ایجاد درگاه پرداخت!", show_alert=True)
            
    except Exception as e:
        await callback.answer(f"❌ خطا: {e}", show_alert=True)

# --- 💳 زیبال ---

@Client.on_callback_query(filters.regex(r"^pay:zibal$"))
async def zibal_payment(client: Client, callback: CallbackQuery):
    """پرداخت با زیبال"""
    if not config.ZIBAL_ENABLED:
        await callback.answer("❌ این روش غیرفعال است", show_alert=True)
        return
    
    user_id = callback.from_user.id
    state = db.fetchone('SELECT * FROM user_states WHERE user_id = ?', (user_id,))
    plan = json.loads(state['data'])
    
    transaction_id = generate_transaction_id()
    amount = plan['price']
    
    db.execute('''
        INSERT INTO transactions (
            transaction_id, user_id, amount, payment_method, 
            plan_days, status, created_at
        ) VALUES (?, ?, ?, 'zibal', ?, 'pending', ?)
    ''', (transaction_id, user_id, amount, plan['days'], int(time.time())))
    
    try:
        url = "https://gateway.zibal.ir/v1/request"
        data = {
            "merchant": config.ZIBAL_MERCHANT,
            "amount": amount * 10,
            "callbackUrl": f"{config.WEBHOOK_URL}/verify/zibal/{transaction_id}",
            "description": f"خرید اشتراک {plan['name']}"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                result = await response.json()
        
        if result['result'] == 100:
            track_id = result['trackId']
            payment_url = f"https://gateway.zibal.ir/start/{track_id}"
            
            db.execute('''
                UPDATE transactions SET payment_data = ? WHERE transaction_id = ?
            ''', (str(track_id), transaction_id))
            
            await callback.message.edit_text(
                f"✅ **لینک پرداخت ساخته شد**\n\n"
                f"💰 مبلغ: {amount:,} تومان\n"
                f"🆔 شناسه: `{transaction_id}`\n\n"
                f"🔗 [پرداخت کنید]({payment_url})",
                disable_web_page_preview=True
            )
        else:
            await callback.answer("❌ خطا در ایجاد درگاه!", show_alert=True)
            
    except Exception as e:
        await callback.answer(f"❌ خطا: {e}", show_alert=True)

# --- 💵 کارت به کارت ---

@Client.on_callback_query(filters.regex(r"^pay:card$"))
async def card_payment(client: Client, callback: CallbackQuery):
    """پرداخت کارت به کارت"""
    if not config.CARD_ENABLED:
        await callback.answer("❌ این روش غیرفعال است", show_alert=True)
        return
    
    user_id = callback.from_user.id
    state = db.fetchone('SELECT * FROM user_states WHERE user_id = ?', (user_id,))
    plan = json.loads(state['data'])
    
    transaction_id = generate_transaction_id()
    amount = plan['price']
    
    db.execute('''
        INSERT INTO transactions (
            transaction_id, user_id, amount, payment_method, 
            plan_days, status, created_at
        ) VALUES (?, ?, ?, 'card', ?, 'pending', ?)
    ''', (transaction_id, user_id, amount, plan['days'], int(time.time())))
    
    text = f"""
💳 **پرداخت کارت به کارت**

💰 **مبلغ قابل پرداخت:** {amount:,} تومان
🆔 **شناسه تراکنش:** `{transaction_id}`

📌 **شماره کارت:**
`{config.CARD_NUMBER}`

📝 **به نام:** {config.CARD_HOLDER}

⚠️ **مهم:**
1. مبلغ را به شماره کارت بالا واریز کنید
2. عکس رسید را ارسال کنید
3. پس از تأیید، اشتراک شما فعال می‌شود

⏳ مدت زمان بررسی: حداکثر ۱ ساعت
    """
    
    await callback.message.edit_text(text, reply_markup=confirm_payment(transaction_id))

# --- تأیید پرداخت کارت به کارت ---

@Client.on_callback_query(filters.regex(r"^confirm_payment:"))
async def confirm_card_payment(client: Client, callback: CallbackQuery):
    """درخواست تأیید پرداخت"""
    transaction_id = callback.data.split(":")[1]
    
    await callback.message.edit_text(
        "📸 **لطفاً عکس رسید واریزی را ارسال کنید**\n\n"
        "✅ فرمت‌های قابل قبول: JPG, PNG\n"
        "⚠️ عکس باید واضح و خوانا باشد"
    )
    
    db.execute('''
        INSERT OR REPLACE INTO user_states (user_id, state, data, updated_at)
        VALUES (?, 'upload_receipt', ?, ?)
    ''', (callback.from_user.id, transaction_id, int(time.time())))
    
    await callback.answer()

@Client.on_message(filters.photo & filters.private)
async def receive_receipt(client: Client, message: Message):
    """دریافت رسید"""
    user_id = message.from_user.id
    state = db.fetchone('SELECT * FROM user_states WHERE user_id = ?', (user_id,))
    
    if not state or state['state'] != 'upload_receipt':
        return
    
    transaction_id = state['data']
    
    # ارسال برای ادمین‌ها
    transaction = db.fetchone('SELECT * FROM transactions WHERE transaction_id = ?', (transaction_id,))
    
    if not transaction:
        await message.reply_text("❌ تراکنش یافت نشد!")
        return
    
    receipt_text = f"""
🧾 **درخواست تأیید پرداخت**

👤 **کاربر:** [{user_id}](tg://user?id={user_id})
🆔 **تراکنش:** `{transaction_id}`
💰 **مبلغ:** {transaction['amount']:,} تومان
⏳ **مدت:** {transaction['plan_days']} روز
📅 **تاریخ:** {time.strftime('%Y/%m/%d %H:%M')}
    """
    
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ تأیید", callback_data=f"approve_payment:{transaction_id}"),
            InlineKeyboardButton("❌ رد", callback_data=f"reject_payment:{transaction_id}")
        ]
    ])
    
    for admin_id in config.ADMIN_IDS:
        try:
            await client.send_photo(
                admin_id,
                message.photo.file_id,
                caption=receipt_text,
                reply_markup=keyboard
            )
        except:
            pass
    
    db.execute('DELETE FROM user_states WHERE user_id = ?', (user_id,))
    
    await message.reply_text(
        "✅ **رسید شما ارسال شد**\n\n"
        "⏳ لطفاً منتظر تأیید ادمین بمانید\n"
        "📢 پس از تأیید، به شما اطلاع‌رسانی می‌شود"
    )

# --- تأیید/رد پرداخت توسط ادمین ---

@Client.on_callback_query(filters.regex(r"^approve_payment:"))
async def approve_payment(client: Client, callback: CallbackQuery):
    """تأیید پرداخت"""
    from utils.decorators import admin_only
    
    if callback.from_user.id not in config.ADMIN_IDS:
        await callback.answer("❌ شما دسترسی ندارید!", show_alert=True)
        return
    
    transaction_id = callback.data.split(":")[1]
    
    transaction = db.fetchone('SELECT * FROM transactions WHERE transaction_id = ?', (transaction_id,))
    
    if not transaction:
        await callback.answer("❌ تراکنش یافت نشد!", show_alert=True)
        return
    
    if transaction['status'] != 'pending':
        await callback.answer("⚠️ این تراکنش قبلاً پردازش شده!", show_alert=True)
        return
    
    # فعال‌سازی اشتراک
    user_id = transaction['user_id']
    days = transaction['plan_days']
    expire_time = int(time.time()) + (days * 86400)
    
    db.execute('''
        UPDATE users 
        SET is_premium = 1, subscription_end = ?
        WHERE user_id = ?
    ''', (expire_time, user_id))
    
    db.execute('''
        UPDATE transactions 
        SET status = 'completed', verified_at = ?
        WHERE transaction_id = ?
    ''', (int(time.time()), transaction_id))
    
    # اطلاع‌رسانی به کاربر
    try:
        await client.send_message(
            user_id,
            f"🎉 **پرداخت شما تأیید شد!**\n\n"
            f"✅ اشتراک {days} روزه شما فعال شد\n"
            f"🆔 شناسه: `{transaction_id}`\n"
            f"📅 انقضا: {time.strftime('%Y/%m/%d', time.localtime(expire_time))}"
        )
    except:
        pass
    
    await callback.message.edit_caption(
        callback.message.caption + "\n\n✅ **تأیید شده توسط ادمین**"
    )
    await callback.answer("✅ پرداخت تأیید شد")

@Client.on_callback_query(filters.regex(r"^reject_payment:"))
async def reject_payment(client: Client, callback: CallbackQuery):
    """رد پرداخت"""
    if callback.from_user.id not in config.ADMIN_IDS:
        await callback.answer("❌ شما دسترسی ندارید!", show_alert=True)
        return
    
    transaction_id = callback.data.split(":")[1]
    
    db.execute('''
        UPDATE transactions 
        SET status = 'rejected', verified_at = ?
        WHERE transaction_id = ?
    ''', (int(time.time()), transaction_id))
    
    transaction = db.fetchone('SELECT user_id FROM transactions WHERE transaction_id = ?', (transaction_id,))
    
    try:
        await client.send_message(
            transaction['user_id'],
            f"❌ **پرداخت شما رد شد**\n\n"
            f"🆔 شناسه: `{transaction_id}`\n\n"
            f"⚠️ دلیل: رسید نامعتبر یا ناخوانا\n"
            f"📞 برای اطلاعات بیشتر با پشتیبانی تماس بگیرید"
        )
    except:
        pass
    
    await callback.message.edit_caption(
        callback.message.caption + "\n\n❌ **رد شده توسط ادمین**"
    )
    await callback.answer("❌ پرداخت رد شد")
