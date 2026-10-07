import telebot
import json
import os
from flask import Flask
from threading import Thread
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = "8497566219:AAHqLm7--Awob0P3BKhitkdxF8lx_5V08Bg"  # अपना बोट टोकन यहाँ रखें
bot = telebot.TeleBot(API_TOKEN)
ADMIN_ID = 8380823727

DATA_FILE = 'ff_stock.json'
PENDING_FILE = 'pending_orders.json'
USERS_FILE = 'users_balance.json'

def load_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def save_data(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Render के लिए Flask सर्वर (Keep-alive)
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# मुख्य डैशबोर्ड मेनू लेआउट
def get_main_menu_markup(user_id):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🛍️ Buy Free Fire IDs", callback_data="buy_ff"),
        InlineKeyboardButton("💰 Add Balance", callback_data="add_balance_menu"),
        InlineKeyboardButton("📦 My Orders", callback_data="my_orders"),
        InlineKeyboardButton("👤 Profile", callback_data="my_profile"),
    )
    markup.add(InlineKeyboardButton("💬 Support", callback_data="support"))
    if user_id == ADMIN_ID:
        markup.add(InlineKeyboardButton("⚙️ Admin Panel (Add ID)", callback_data="admin_panel"))
    return markup

@bot.message_handler(commands=['start'])
def menu(message):
    user = message.from_user
    user_id_str = str(user.id)
    
    # अगर कोई पेंडिंग ऑर्डर था तो उसे क्लियर करें
    pending = load_data(PENDING_FILE)
    if user_id_str in pending:
        del pending[user_id_str]
        save_data(PENDING_FILE, pending)

    users_data = load_data(USERS_FILE)
    if user_id_str not in users_data:
        users_data[user_id_str] = {"balance": 0.0, "orders": []}
        save_data(USERS_FILE, users_data)

    balance = users_data[user_id_str].get("balance", 0.0)
    markup = get_main_menu_markup(user.id)

    text = (
        "⚡ **OFFICIAL GAMING ID STORE** ⚡\n"
        "────────────────────────\n"
        f"👋 Hello, {user.first_name}!\n\n"
        "💎 Premium digital keys, instant delivery & secure store.\n\n"
        "✨ Wide product catalog\n"
        "⚡ Instant key delivery\n"
        "💳 Multiple payment gateways\n"
        f"💵 **Wallet Balance:** ₹{balance}\n\n"
        "👇 *Tap any button below to begin:*"
    )
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    user = call.from_user
    user_id_str = str(user.id)
    users_data = load_data(USERS_FILE)
    
    if user_id_str not in users_data:
        users_data[user_id_str] = {"balance": 0.0, "orders": []}
        save_data(USERS_FILE, users_data)

    if call.data == "my_profile":
        balance = users_data[user_id_str]["balance"]
        orders_count = len(users_data[user_id_str]["orders"])
        
        text = (
            f"👤 **USER PROFILE**\n"
            f"────────────────────────\n"
            f"🆔 User ID: `{user.id}`\n"
            f"👤 Name: {user.first_name}\n"
            f"💰 Wallet Balance: ₹{balance}\n"
            f"📦 Total Orders: {orders_count}\n"
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu"))
        bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "add_balance_menu":
        text = (
            "💰 **ADD BALANCE TO WALLET**\n"
            "────────────────────────\n"
            "बैलेंस ऐड करने के लिए एडमिन से संपर्क करें:\n"
            "👉 @Admin"
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu"))
        bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "my_orders":
        orders = users_data[user_id_str]["orders"]
        if not orders:
            text = "📦 **MY ORDERS**\n────────────────────────\nआपने अभी तक कोई आर्डर नहीं किया है।"
        else:
            text = "📦 **YOUR RECENT ORDERS**\n────────────────────────\n"
            for idx, order in enumerate(orders, 1):
                text += f"{idx}. {order}\n"

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu"))
        bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "buy_ff":
        stock = load_data(DATA_FILE)
        available_items = {k: v for k, v in stock.items() if v.get('status') == 'Available'}
        if not available_items:
            bot.answer_callback_query(call.id, "❌ अभी कोई आईडी उपलब्ध नहीं है!", show_alert=True)
            return

        markup = InlineKeyboardMarkup(row_width=1)
        for item_id, data in available_items.items():
            markup.add(InlineKeyboardButton(f"🆔 Level {data['level']} | UID {data['bundles']} | 💰 ₹{data['price']}", callback_data=f"buy_{item_id}"))
        markup.add(InlineKeyboardButton("« Main Menu", callback_data="main_menu"))
        
        bot.edit_message_text("💎 **AVAILABLE FREE FIRE MAX IDS**\n\nClick on any ID below to purchase:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data.startswith("buy_"):
        item_id = call.data.replace("buy_", "")
        stock = load_data(DATA_FILE)
        if item_id not in stock or stock[item_id].get('status') != 'Available':
            bot.answer_callback_query(call.id, "❌ यह आईडी बिक चुकी है या उपलब्ध नहीं है!", show_alert=True)
            return

        item = stock[item_id]
        
        # पेंडिंग ऑर्डर में सेव करें ताकि यूजर चैट में रिडीम कोड भेज सके
        pending = load_data(PENDING_FILE)
        pending[user_id_str] = item_id
        save_data(PENDING_FILE, pending)

        pay_text = (
            f"🛒 **ID BOOKING DETAILS**\n"
            f"────────────────────────\n"
            f"🔥 Level: {item['level']}\n"
            f"📦 Collection: UID {item['bundles']}\n"
            f"💵 Price: ₹{item['price']}\n\n"
            f"📌 **How to Purchase:**\n"
            f"1️⃣ Purchase a Google Play Redeem Code worth ₹{item['price']}.\n"
            f"2️⃣ Now type and send your Google Play Redeem Code here in chat!\n\n"
            f"💡 **Example Format:**\n"
            f"ABCD1234EFGH5678"
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("« Back", callback_data="buy_ff"))
        bot.edit_message_text(pay_text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "admin_panel":
        if user.id != ADMIN_ID:
            return
        admin_text = (
            "⚙️ **ADMIN PANEL**\n\n"
            "• आईडी जोड़ने के लिए:\n"
            "`/addff [Level] | [UID/Bundle] | [Price]`\n\n"
            "• बैलेंस जोड़ने के लिए:\n"
            "`/addbalance [user_id] [amount]`\n\n"
            "• आईडी डिलीवर करने के लिए:\n"
            "`/deliverff [buyer_id] [item_id]`"
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu"))
        bot.edit_message_text(admin_text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "support":
        text = (
            "💬 **CUSTOMER SUPPORT**\n"
            "────────────────────────\n"
            "मदद के लिए संपर्क करें: @Admin"
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu"))
        bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "main_menu":
        pending = load_data(PENDING_FILE)
        if user_id_str in pending:
            del pending[user_id_str]
            save_data(PENDING_FILE, pending)

        balance = users_data[user_id_str]["balance"]
        markup = get_main_menu_markup(user.id)
        text = (
            "👇 *Main Dashboard Menu:*\n"
            "⚡ **OFFICIAL GAMING ID STORE** ⚡\n"
            "────────────────────────\n"
            f"👋 Hello, {user.first_name}!\n\n"
            f"💵 **Wallet Balance:** ₹{balance}\n\n"
            "👇 *Tap any button below to begin:*"
        )
        bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

# यूजर द्वारा रिडीम कोड चैट में भेजने पर हैंडल करना (इसमें यूजरनेम, आईडी, और पूरी डिटेल एडमिन को जाएगी)
@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    user = message.from_user
    if user.id == ADMIN_ID:
        return

    pending = load_data(PENDING_FILE)
    if str(user.id) not in pending:
        return

    item_id = pending[str(user.id)]
    redeem_code = message.text.strip()

    stock = load_data(DATA_FILE)
    item = stock.get(item_id)

    # पेंडिंग लिस्ट से हटा दें
    del pending[str(user.id)]
    save_data(PENDING_FILE, pending)

    if item:
        item_desc = f"Level {item['level']} | UID {item['bundles']} (₹{item['price']})"
    else:
        item_desc = "Unknown Item"

    username = f"@{user.username}" if user.username else "No Username"

    # एडमिन के पास यूजर की पूरी डिटेल भेजने का फॉर्मेट
    admin_msg = (
        f"🔔 **NEW REDEEM CODE RECEIVED!**\n"
        f"────────────────────────\n"
        f"👤 Buyer Name: {user.first_name}\n"
        f"🔗 Username: {username}\n"
        f"🆔 User ID: `{user.id}`\n"
        f"📦 Item Details: {item_desc}\n"
        f"🎟️ Redeem Code: `{redeem_code}`\n\n"
        f"👉 आईडी डिलीवर करने के लिए नीचे दिए गए कमांड पर क्लिक करें:\n"
        f"`/deliverff {user.id} {item_id}`"
    )
    bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")
    bot.reply_to(message, "✅ आपका रिडीम कोड एडमिन को सफलतापूर्वक भेज दिया गया है! जाँच के बाद आपको आईडी मिल जाएगी।")

# एडमिन द्वारा आईडी जोड़ने का कमांड
@bot.message_handler(commands=['addff'])
def add_ff(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        content = message.text.replace('/addff', '').strip()
        parts = content.split('|')
        level = parts[0].strip()
        bundles = parts[1].strip()
        price = parts[2].strip()

        stock = load_data(DATA_FILE)
        item_id = str(len(stock) + 1)
        while item_id in stock:
            item_id = str(int(item_id) + 1)

        stock[item_id] = {
            "level": level,
            "bundles": bundles,
            "price": price,
            "status": "Available"
        }
        save_data(DATA_FILE, stock)
        bot.reply_to(message, f"✅ ID successfully added with ID: `{item_id}`", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, "❌ गलत फॉर्मेट! इस्तेमाल करें:\n`/addff [Level] | [UID] | [Price]`", parse_mode="Markdown")

# एडमिन द्वारा बैलेंस जोड़ने का कमांड
@bot.message_handler(commands=['addbalance'])
def add_balance_cmd(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        parts = message.text.split()
        target_id = parts[1]
        amount = float(parts[2])
        
        users_data = load_data(USERS_FILE)
        if target_id not in users_data:
            users_data[target_id] = {"balance": 0.0, "orders": []}
        
        users_data[target_id]["balance"] += amount
        save_data(USERS_FILE, users_data)
        
        bot.reply_to(message, f"✅ Successfully added ₹{amount} to user `{target_id}`.", parse_mode="Markdown")
        bot.send_message(int(target_id), f"🎉 Your wallet has been credited with ₹{amount} by Admin!")
    except Exception as e:
        bot.reply_to(message, "❌ फॉर्मेट गलत है! इस्तेमाल करें: `/addbalance [user_id] [amount]`", parse_mode="Markdown")

# एडमिन द्वारा आईडी डिलीवर करने का कमांड
@bot.message_handler(commands=['deliverff'])
def deliver_ff(message):
    if message.from_user.id != ADMIN_ID:
        return

    args = message.text.split()
    if len(args) < 3:
        bot.reply_to(message, "❌ गलत फॉर्मेट! इस्तेमाल करें: `/deliverff [buyer_id] [item_id]`", parse_mode="Markdown")
        return

    try:
        buyer_id = int(args[1])
        item_id = str(args[2])
    except ValueError:
        bot.reply_to(message, "❌ आईडी या यूजर आईडी नंबर में होनी चाहिए!")
        return

    stock = load_data(DATA_FILE)
    if item_id not in stock or stock[item_id]['status'] == 'Sold':
        bot.reply_to(message, "❌ यह आईडी मौजूद नहीं है या पहले ही बिक चुकी है!")
        return

    stock[item_id]['status'] = 'Sold'
    save_data(DATA_FILE, stock)

    item = stock[item_id]
    
    # यूजर के आर्डर हिस्ट्री में जोड़ें
    users_data = load_data(USERS_FILE)
    buyer_id_str = str(buyer_id)
    if buyer_id_str not in users_data:
        users_data[buyer_id_str] = {"balance": 0.0, "orders": []}
    
    order_info = f"Level {item['level']} | UID {item['bundles']} (₹{item['price']})"
    users_data[buyer_id_str]["orders"].append(order_info)
    save_data(USERS_FILE, users_data)

    # खरीदार को आईडी की डिटेल्स भेजना
    try:
        bot.send_message(
            buyer_id,
            f"🎉 **CONGRATULATIONS! Deal Successful**\n"
            f"────────────────────────\n"
            f"🔥 Level: {item['level']}\n"
            f"📦 UID & Details: {item['bundles']}\n"
            f"💵 Price: ₹{item['price']}\n\n"
            f"✨ धन्यवाद हमारे स्टोर से खरीदारी करने के लिए!"
        )
    except Exception as e:
        pass

    bot.reply_to(message, f"✅ आईडी सफलतापूर्वक खरीदार (`{buyer_id}`) को डिलीवर कर दी गई है!", parse_mode="Markdown")

if __name__ == '__main__':
    keep_alive()
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)
    
                           
    
    
        
    

    
