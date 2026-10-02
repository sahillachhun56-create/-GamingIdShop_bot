import telebot
import sqlite3
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = "8497566219:AAEXaU0YUHIDPS8WR-Oa0cOzRUX1qXiLooE"  # अपना टोकन यहाँ रखें
bot = telebot.TeleBot(API_TOKEN)
ADMIN_ID = 8380823727

def init_db():
    conn = sqlite3.connect('ff_id_store.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level TEXT,
            bundles TEXT,
            price REAL,
            status TEXT DEFAULT 'Available'
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@bot.message_handler(commands=['start', 'menu'])
def menu(message):
    user_id = message.from_user.id
    markup = InlineKeyboardMarkup(row_width=1)
    
    markup.add(
        InlineKeyboardButton("🔥 Buy Free Fire Max IDs", callback_data="buy_ff"),
        InlineKeyboardButton("💬 Customer Support", callback_data="support")
    )
    
    if user_id == ADMIN_ID:
        markup.add(InlineKeyboardButton("⚙️ Admin Panel (Add ID)", callback_data="admin_panel"))

    text = (
        "⚡ **OFFICIAL GAMING ID STORE** ⚡\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🎯 *Trusted & 100% Secure Free Fire Max IDs Marketplace!*\n\n"
        "💳 **Payment Mode:** Google Play Redeem Code\n"
        "🛡️ **Guarantee:** Instant Delivery & Verified Accounts\n\n"
        "👇 **Select an option below to get started:**"
    )
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    user = call.from_user
    if call.data == "buy_ff":
        conn = sqlite3.connect('ff_id_store.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT id, level, bundles, price FROM stock WHERE status='Available'")
        items = cursor.fetchall()
        conn.close()
        
        if not items:
            bot.answer_callback_query(call.id, "⚠️ Sorry, no IDs are currently available in stock!", show_alert=True)
            return
            
        markup = InlineKeyboardMarkup(row_width=1)
        for item in items:
            item_id, level, bundles, price = item
            markup.add(InlineKeyboardButton(f"🆔 Level {level} | 📦 {bundles} | 💰 ₹{price}", callback_data=f"buy_{item_id}"))
        markup.add(InlineKeyboardButton("« Back to Main Menu", callback_data="main_menu"))
        
        bot.edit_message_text(
            "💎 **AVAILABLE FREE FIRE MAX IDS**\n\n"
            "Click on any ID below to check details and buy:",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode='Markdown',
            reply_markup=markup
        )
        
    elif call.data.startswith("buy_"):
        item_id = call.data.replace("buy_", "")
        conn = sqlite3.connect('ff_id_store.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT level, bundles, price FROM stock WHERE id=? AND status='Available'", (item_id,))
        item = cursor.fetchone()
        conn.close()
        
        if not item:
            bot.answer_callback_query(call.id, "❌ This ID has already been sold!", show_alert=True)
            return
            
        level, bundles, price = item
        pay_text = (
            f"🛒 **ID BOOKING DETAILS**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔥 **Level:** {level}\n"
            f"📦 **Collection:** {bundles}\n"
            f"💵 **Price:** ₹{price}\n\n"
            f"📌 **How to Purchase:**\n"
            f"1️⃣ Purchase a **Google Play Redeem Code** worth ₹{price} from any store.\n"
            f"2️⃣ Send the code in chat using this command:\n\n"
            f"👉 `/redeem {item_id} [Your Google Play Code]`"
        )
        bot.send_message(call.message.chat.id, pay_text, parse_mode='Markdown')
        
    elif call.data == "admin_panel":
        if user.id != ADMIN_ID:
            bot.answer_callback_query(call.id, "⚠️ Access Denied! Admin only.", show_alert=True)
            return
        admin_text = (
            "⚙️ **ADMIN CONTROL PANEL**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "To add a new ID, use the format below:\n\n"
            "`/addff [Level] | [Bundles] | [Price]`\n\n"
            "**Example:**\n"
            "`/addff 65 | Cobra Bundle, Max Gun | 499`"
        )
        bot.send_message(call.message.chat.id, admin_text, parse_mode='Markdown')
        
    elif call.data == "main_menu":
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("🔥 Buy Free Fire Max IDs", callback_data="buy_ff"),
            InlineKeyboardButton("💬 Customer Support", callback_data="support")
        )
        if user.id == ADMIN_ID:
            markup.add(InlineKeyboardButton("⚙️ Admin Panel (Add ID)", callback_data="admin_panel"))
            
        bot.edit_message_text(
            "⚡ **OFFICIAL GAMING ID STORE** ⚡\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🎯 *Trusted & 100% Secure Free Fire Max IDs Marketplace!*",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode='Markdown',
            reply_markup=markup
        )
        
    elif call.data == "support":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "💬 For support, contact: @Momshad_00")

@bot.message_handler(commands=['addff'])
def add_ff(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        content = message.text.replace('/addff', '').strip()
        parts = content.split('|')
        level, bundles, price = parts[0].strip(), parts[1].strip(), float(parts[2].strip())
        
        conn = sqlite3.connect('ff_id_store.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO stock (level, bundles, price, status) VALUES (?, ?, ?, 'Available')", (level, bundles, price))
        conn.commit()
        conn.close()
        
        bot.reply_to(message, f"✅ ID successfully added!\n🔥 Level: {level}\n💰 Price: ₹{price}")
    except Exception as e:
        bot.reply_to(message, f"❌ Invalid format! Use correct format:\n`/addff 65 | Bundle Name | 499`", parse_mode='Markdown')

@bot.message_handler(commands=['redeem'])
def send_redeem(message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        bot.reply_to(message, "❌ Correct usage:\n`/redeem [ID] [Google Play Code]`", parse_mode='Markdown')
        return
    item_id, redeem_code, user = args[1], args[2], message.from_user
    
    admin_msg = (
        f"🔔 **NEW PAYMENT RECEIVED!**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **Buyer:** {user.first_name} (ID: `{user.id}`)\n"
        f"🆔 **Item ID:** `{item_id}`\n"
        f"🎟️ **Redeem Code:** `{redeem_code}`\n\n"
        f"👉 To deliver this ID, send command:\n"
        f"`/deliverff {user.id} {item_id}`"
    )
    bot.send_message(ADMIN_ID, admin_msg, parse_mode='Markdown')
    bot.reply_to(message, "✅ Your redeem code has been sent to the admin successfully! You will receive the ID after verification.")

@bot.message_handler(commands=['deliverff'])
def deliver_ff(message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split()
    if len(args) < 3:
        bot.reply_to(message, "❌ Correct format: `/deliverff [User_ID] [Item_ID]`", parse_mode='Markdown')
        return
        
    buyer_id, item_id = int(args[1]), args[2]
    conn = sqlite3.connect('ff_id_store.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT level, bundles FROM stock WHERE id=? AND status='Available'", (item_id,))
    item = cursor.fetchone()
    
    if not item:
        conn.close()
        bot.reply_to(message, "❌ This ID is either sold or invalid!")
        return
        
    level, bundles = item
    cursor.execute("UPDATE stock SET status='Sold' WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
    
    bot.send_message(
        buyer_id, 
        f"🎉 **CONGRATULATIONS! Deal Successful.**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔥 **Level:** {level}\n"
        f"📦 **ID & Password Details:**\n`{bundles}`", 
        parse_mode='Markdown'
    )
    bot.reply_to(message, "✅ ID successfully delivered to the user!")

if __name__ == '__main__':
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)
    
