import telebot
import sqlite3
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '8497566219:AAHjz8OLSm06Ksrl_fwAfGVhVGOBaH6TxOM'
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
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🔥 Buy Free Fire IDs", callback_data="buy_ff"),
        InlineKeyboardButton("➕ Add FF ID (Admin)", callback_data="admin_add"),
        InlineKeyboardButton("💬 Support", callback_data="support")
    )
    text = (
        "🔥 <b>OFFICIAL FREE FIRE ID STORE</b> 🔥\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "बेस्ट और सुरक्षित फ्री फायर मैक्स आईडी खरीदें!\n"
        "<i>(Payment Mode: Google Play Redeem Code)</i>\n\n"
        "नीचे दिए गए बटन से शुरुआत करें:"
    )
    bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=markup)

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
            bot.answer_callback_query(call.id, "फिलहाल कोई फ्री फायर आईडी स्टॉक में नहीं है!", show_alert=True)
            return
        markup = InlineKeyboardMarkup(row_width=1)
        for item in items:
            item_id, level, bundles, price = item
            markup.add(InlineKeyboardButton(f"🆔 Level {level} | {bundles} - ₹{price}", callback_data=f"buy_{item_id}"))
        markup.add(InlineKeyboardButton("« Back to Menu", callback_data="main_menu"))
        bot.edit_message_text(
            "🔥 <b>AVAILABLE FREE FIRE IDS</b>\n\nखरीदने के लिए नीचे दी गई आईडी पर क्लिक करें:",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode='HTML',
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
            bot.answer_callback_query(call.id, "यह आईडी पहले ही बिक चुकी है!", show_alert=True)
            return
        level, bundles, price = item
        pay_text = (
            f"🎁 <b>GOOGLE PLAY REDEEM CODE PAYMENT</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🔥 <b>Level:</b> {level}\n"
            f"📦 <b>Items/Bundles:</b> {bundles}\n"
            f"💰 <b>Price:</b> ₹{price}\n\n"
            f"1️⃣ कृपया ₹{price} का <b>Google Play Redeem Code</b> खरीदें।\n"
            f"2️⃣ रिडीम कोड भेजने के लिए यह कमांड इस्तेमाल करें:\n"
            f"👉 <code>/redeem {item_id} [Google Play Code]</code>"
        )
        bot.send_message(call.message.chat.id, pay_text, parse_mode='HTML')
    elif call.data == "admin_add":
        if user.id != ADMIN_ID:
            bot.answer_callback_query(call.id, "आप एडमिन नहीं हैं!", show_alert=True)
            return
        bot.send_message(call.message.chat.id, "➕ <b>फॉर्मेट:</b> <code>/addff [Level] | [Details] | [Price]</code>", parse_mode='HTML')
    elif call.data == "main_menu":
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🔥 Buy Free Fire IDs", callback_data="buy_ff"),
            InlineKeyboardButton("➕ Add FF ID (Admin)", callback_data="admin_add"),
            InlineKeyboardButton("💬 Support", callback_data="support")
        )
        bot.edit_message_text("🔥 <b>OFFICIAL FREE FIRE ID STORE</b> 🔥", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='HTML', reply_markup=markup)
    elif call.data == "support":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "💬 संपर्क करें: @Momshad_00")

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
        bot.reply_to(message, f"✅ आईडी जुड़ गई! Level: {level}, Price: ₹{price}")
    except Exception as e:
        bot.reply_to(message, f"❌ एरर: {str(e)}")

@bot.message_handler(commands=['redeem'])
def send_redeem(message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        bot.reply_to(message, "❌ इस्तेमाल: <code>/redeem [ID] [Code]</code>", parse_mode='HTML')
        return
    item_id, redeem_code, user = args[1], args[2], message.from_user
    admin_msg = f"🔔 <b>NEW REDEEM CODE</b>\nBuyer: {user.first_name} (ID: <code>{user.id}</code>)\nItem ID: <code>{item_id}</code>\nCode: <code>{redeem_code}</code>\n👉 डिलीवर करें: <code>/deliverff {user.id} {item_id}</code>"
    bot.send_message(ADMIN_ID, admin_msg, parse_mode='HTML')
    bot.reply_to(message, "✅ कोड एडमिन को भेज दिया गया है!")

@bot.message_handler(commands=['deliverff'])
def deliver_ff(message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split()
    buyer_id, item_id = int(args[1]), args[2]
    conn = sqlite3.connect('ff_id_store.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT level, bundles FROM stock WHERE id=? AND status='Available'", (item_id,))
    item = cursor.fetchone()
    if not item:
        conn.close()
        bot.reply_to(message, "❌ आईडी उपलब्ध नहीं है!")
        return
    level, bundles = item
    cursor.execute("UPDATE stock SET status='Sold' WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
    bot.send_message(buyer_id, f"🎉 <b>PURCHASE SUCCESSFUL!</b>\nLevel: {level}\nDetails: <code>{bundles}</code>", parse_mode='HTML')
    bot.reply_to(message, "✅ सफलतापूर्वक डिलीवर हो गई!")

if __name__ == '__main__':
    bot.infinity_polling(skip_pending=True)
    
