import telebot
import sqlite3
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = "8497566219:AAHviARd-H7Soc0I-dfIku4eshQWwt3FdiM"
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
    
    # मुख्य विकल्प
    markup.add(
        InlineKeyboardButton("🔥 उपलब्ध फ्री फायर मैक्स आईडी देखें", callback_data="buy_ff"),
        InlineKeyboardButton("💬 सहायता और सपोर्ट", callback_data="support")
    )
    
    # अगर यूजर एडमिन है, तभी उसे एडमिन पैनल का बटन दिखेगा
    if user_id == ADMIN_ID:
        markup.add(InlineKeyboardButton("⚙️ एडमिन पैनल (आईडी जोड़ें)", callback_data="admin_panel"))

    text = (
        "⚡ <b>OFFICIAL GAMING ID STORE</b> ⚡\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🎯 <i>भरोसेमंद और सुरक्षित फ्री फायर मैक्स आईडी का सबसे बड़ा ठिकाना!</i>\n\n"
        "💳 <b>पेमेंट का तरीका:</b> Google Play Redeem Code\n"
        "🛡️ <b>गारंटी:</b> 100% सुरक्षित और फास्ट डिलीवरी\n\n"
        "👇 <b>नीचे दिए गए बटन से अपनी मनपसंद आईडी चुनें:</b>"
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
            bot.answer_callback_query(call.id, "⚠️ क्षमा करें, फिलहाल कोई भी आईडी स्टॉक में नहीं है!", show_alert=True)
            return
            
        markup = InlineKeyboardMarkup(row_width=1)
        for item in items:
            item_id, level, bundles, price = item
            markup.add(InlineKeyboardButton(f"🆔 Level {level} | 📦 {bundles} | 💰 ₹{price}", callback_data=f"buy_{item_id}"))
        markup.add(InlineKeyboardButton("« मुख्य मेनू पर जाएं", callback_data="main_menu"))
        
        bot.edit_message_text(
            "💎 <b>उपलब्ध फ्री फायर मैक्स आईडीज़</b>\n\n"
            "खरीदने के लिए नीचे दी गई किसी भी आईडी पर क्लिक करें:",
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
            bot.answer_callback_query(call.id, "❌ यह आईडी पहले ही बिक चुकी है!", show_alert=True)
            return
            
        level, bundles, price = item
        pay_text = (
            f"🛒 <b>आईडी बुकिंग विवरण</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔥 <b>लेवल:</b> {level}\n"
            f"📦 <b>कलेक्शन:</b> {bundles}\n"
            f"💵 <b>कीमत:</b> ₹{price}\n\n"
            f"📌 <b>खरीदने की प्रक्रिया:</b>\n"
            f"1️⃣ किसी भी स्टोर से ₹{price} का <b>Google Play Redeem Code</b> खरीदें।\n"
            f"2️⃣ कोड भेजने के लिए चैट में यह कमांड भेजें:\n\n"
            f"👉 <code>/redeem {item_id} [यहाँ अपना गूगल प्ले कोड लिखें]</code>"
        )
        bot.send_message(call.message.chat.id, pay_text, parse_mode='HTML')
        
    elif call.data == "admin_panel":
        if user.id != ADMIN_ID:
            bot.answer_callback_query(call.id, "⚠️ यह केवल एडमिन के लिए है!", show_alert=True)
            return
        admin_text = (
            "⚙️ <b>एडमिन कंट्रोल पैनल</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "नई आईडी जोड़ने के लिए इस फॉर्मेट का उपयोग करें:\n\n"
            "<code>/addff [Level] | [Bundles] | [Price]</code>\n\n"
            "<b>उदाहरण:</b>\n"
            "<code>/addff 65 | Cobra Bundle, Max Gun | 499</code>"
        )
        bot.send_message(call.message.chat.id, admin_text, parse_mode='HTML')
        
    elif call.data == "main_menu":
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("🔥 उपलब्ध फ्री फायर मैक्स आईडी देखें", callback_data="buy_ff"),
            InlineKeyboardButton("💬 सहायता और सपोर्ट", callback_data="support")
        )
        if user.id == ADMIN_ID:
            markup.add(InlineKeyboardButton("⚙️ एडमिन पैनल (आईडी जोड़ें)", callback_data="admin_panel"))
            
        bot.edit_message_text(
            "⚡ <b>OFFICIAL GAMING ID STORE</b> ⚡\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🎯 <i>भरोसेमंद और सुरक्षित फ्री फायर मैक्स आईडी का सबसे बड़ा ठिकाना!</i>",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode='HTML',
            reply_markup=markup
        )
        
    elif call.data == "support":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "💬 सहायता के लिए संपर्क करें: @Momshad_00")

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
        
        bot.reply_to(message, f"✅ सफलतापूर्व आईडी जोड़ दी गई है!\n🔥 Level: {level}\n💰 Price: ₹{price}")
    except Exception as e:
        bot.reply_to(message, f"❌ फॉर्मेट गलत है! सही तरीका इस्तेमाल करें:\n<code>/addff 65 | Bundle Name | 499</code>", parse_mode='HTML')

@bot.message_handler(commands=['redeem'])
def send_redeem(message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        bot.reply_to(message, "❌ सही तरीका उपयोग करें:\n<code>/redeem [ID] [Google Play Code]</code>", parse_mode='HTML')
        return
    item_id, redeem_code, user = args[1], args[2], message.from_user
    
    admin_msg = (
        f"🔔 <b>नया पेमेंट प्राप्त हुआ!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>खरीदार:</b> {user.first_name} (ID: <code>{user.id}</code>)\n"
        f"🆔 <b>आइटम आईडी:</b> <code>{item_id}</code>\n"
        f"🎟️ <b>रिडीम कोड:</b> <code>{redeem_code}</code>\n\n"
        f"👉 आईडी डिलीवर करने के लिए यह कमांड भेजें:\n"
        f"<code>/deliverff {user.id} {item_id}</code>"
    )
    bot.send_message(ADMIN_ID, admin_msg, parse_mode='HTML')
    bot.reply_to(message, "✅ आपका रिडीम कोड एडमिन के पास सफलतापूर्वक भेज दिया गया है! जाँच के बाद आपको आईडी मिल जाएगी।")

@bot.message_handler(commands=['deliverff'])
def deliver_ff(message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split()
    if len(args) < 3:
        bot.reply_to(message, "❌ सही फॉर्मेट: <code>/deliverff [User_ID] [Item_ID]</code>", parse_mode='HTML')
        return
        
    buyer_id, item_id = int(args[1]), args[2]
    conn = sqlite3.connect('ff_id_store.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT level, bundles FROM stock WHERE id=? AND status='Available'", (item_id,))
    item = cursor.fetchone()
    
    if not item:
        conn.close()
        bot.reply_to(message, "❌ यह आईडी या तो बिक चुकी है या गलत है!")
        return
        
    level, bundles = item
    cursor.execute("UPDATE stock SET status='Sold' WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
    
    bot.send_message(
        buyer_id, 
        f"🎉 <b>बधाई हो! आपकी डील सफल रही।</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔥 <b>लेवल:</b> {level}\n"
        f"📦 <b>आईडी पासवर्ड / विवरण:</b>\n<code>{bundles}</code>", 
        parse_mode='HTML'
    )
    bot.reply_to(message, "✅ यूजर को सफलतापूर्वक आईडी डिलीवर कर दी गई है!")

if __name__ == '__main__':
    bot.infinity_polling(skip_pending=True)
        
    
