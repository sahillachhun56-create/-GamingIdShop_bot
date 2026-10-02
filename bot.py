import telebot
import sqlite3
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '8497566219:AAFPKrnggpb_CkjoPH2saUp8NDTjgwIwrBg'  # यहाँ अपना बोट टोकन डालें
bot = telebot.TeleBot(API_TOKEN)

ADMIN_ID = 8380823727  # आपकी एडमिन आईडी

# --- डेटाबेस सेटअप ---
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

# --- मुख्य मेनू ---
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
        "बेस्ट और सुरक्षित फ्री फायर मैक्स (Free Fire Max) आईडी खरीदें!\n"
        "<i>(Payment Mode: Google Play Redeem Code)</i>\n\n"
        "नीचे दिए गए बटन से शुरुआत करें:"
    )
    bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=markup)

# --- बटन और कॉलबैक हैंडलर ---
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
            f"👉 <code>/redeem {item_id} [Google Play Code]</code>\n\n"
            f"<i>उदाहरण: /redeem {item_id} ABC12XYZ34...</i>"
        )
        bot.send_message(call.message.chat.id, pay_text, parse_mode='HTML')

    elif call.data == "admin_add":
        if user.id != ADMIN_ID:
            bot.answer_callback_query(call.id, "आप एडमिन नहीं हैं!", show_alert=True)
            return
        bot.send_message(
            call.message.chat.id,
            "➕ <b>फ्री फायर आईडी जोड़ने का फॉर्मेट:</b>\n\n<code>/addff [Level] | [Bundles/Details] | [Price]</code>\n\n<i>उदाहरण: /addff 72 | Cobra MP40, Old Elite Pass | 499</i>",
            parse_mode='HTML'
        )

    elif call.data == "main_menu":
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🔥 Buy Free Fire IDs", callback_data="buy_ff"),
            InlineKeyboardButton("➕ Add FF ID (Admin)", callback_data="admin_add"),
            InlineKeyboardButton("💬 Support", callback_data="support")
        )
        bot.edit_message_text(
            "🔥 <b>OFFICIAL FREE FIRE ID STORE</b> 🔥\n\nनीचे दिए गए बटन से शुरुआत करें:",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode='HTML',
            reply_markup=markup
        )

    elif call.data == "support":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "💬 सहायता के लिए संपर्क करें: @Momshad_00")

# --- एडमिन द्वारा स्टॉक जोड़ने का कमांड ---
@bot.message_handler(commands=['addff'])
def add_ff(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ केवल एडमिन!")
        return
    try:
        content = message.text.replace('/addff', '').strip()
        parts = content.split('|')
        if len(parts) < 3:
            bot.reply_to(message, "❌ गलत फॉर्मेट! इस्तेमाल करें: <code>/addff [Level] | [Details] | [Price]</code>", parse_mode='HTML')
            return
        level = parts[0].strip()
        bundles = parts[1].strip()
        price = float(parts[2].strip())

        conn = sqlite3.connect('ff_id_store.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO stock (level, bundles, price, status) VALUES (?, ?, ?, 'Available')", (level, bundles, price))
        conn.commit()
        conn.close()

        bot.reply_to(message, f"✅ फ्री फायर आईडी स्टॉक में जुड़ गई!\n🔥 Level: {level}\n💰 Price: ₹{price}")
    except Exception as ec:
        bot.reply_to(message, f"❌ एरर: {str(ec)}")

# --- यूजर द्वारा रिडीम कोड भेजने का कमांड ---
@bot.message_handler(commands=['redeem'])
def send_redeem(message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        bot.reply_to(message, "❌ गलत फॉर्मेट! इस्तेमाल: <code>/redeem [ID] [Google Play Code]</code>", parse_mode='HTML')
        return
    item_id = args[1]
    redeem_code = args[2]
    user = message.from_user

    admin_msg = (
        "🔔 <b>NEW GOOGLE PLAY REDEEM CODE SUBMITTED</b>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Buyer:</b> {user.first_name} (@{user.username if user.username else 'None'})\n"
        f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
        f"📦 <b>Item ID:</b> <code>{item_id}</code>\n"
        f"🎁 <b>Redeem Code:</b> <code>{redeem_code}</code>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"👉 कोड चेक करने के बाद आईडी डिलीवर करने के लिए भेजें:\n<code>/deliverff {user.id} {item_id}</code>"
    )
    bot.send_message(ADMIN_ID, admin_msg, parse_mode='HTML')
    bot.reply_to(message, "✅ आपका गूगल प्ले रिडीम कोड एडमिन के पास भेज दिया गया है। चेक होने के बाद आईडी आपको मिल जाएगी!")

# --- एडमिन द्वारा आईडी डिलीवर करने का कमांड ---
@bot.message_handler(commands=['deliverff'])
def deliver_ff(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ केवल एडमिन!")
        return
    args = message.text.split()
    if len(args) < 3:
        bot.reply_to(message, "❌ इस्तेमाल: <code>/deliverff [Buyer ID] [Item ID]</code>", parse_mode='HTML')
        return
    buyer_id = int(args[1])
    item_id = args[2]

    conn = sqlite3.connect('ff_id_store.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT level, bundles FROM stock WHERE id=? AND status='Available'", (item_id,))
    item = cursor.fetchone()
    if not item:
        conn.close()
        bot.reply_to(message, "❌ आईडी उपलब्ध नहीं है या बिक चुकी है!")
        return

    level, bundles = item
    cursor.execute("UPDATE stock SET status='Sold' WHERE id=?", (item_id,))
    conn.commit()
    conn.close()

    try:
        bot.send_message(
            buyer_id,
            f"🎉 <b>FREE FIRE ID PURCHASE SUCCESSFUL!</b>\n\n🔥 <b>Level:</b> {level}\n📦 <b>Items/Details:</b> <code>{bundles}</code>\n\n<i>कृपया लॉगिन करके तुरंत पासवर्ड और बाइंडिंग बदल लें!</i>",
            parse_mode='HTML'
        )
        bot.reply_to(message, f"✅ आईडी सफलतापूर्वक यूजर (ID: {buyer_id}) को डिलीवर कर दी गई है!")
    except Exception as e:
        bot.reply_to(message, f"❌ भेजने में एरर: {str(e)}")

# --- बोट रन करने का लूप ---
if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"Error: {e}")
            import time
            time.sleep(5)
