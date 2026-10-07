import telebot
import json
import os
from flask import Flask
from threading import Thread
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = "8497566219:AAE5CDisuQFee1g7pYlAiug1mKo7ERzeKjo"  # Put your bot token here
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

# Flask Server for Render (Keep-alive)
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# Main Dashboard Menu Layout with Colorful Design
def get_main_menu_markup(user_id):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🛒 Buy Free Fire IDs", callback_data="buy_ff"),
        InlineKeyboardButton("💎 Add Balance", callback_data="add_balance_menu"),
    )
    markup.add(
        InlineKeyboardButton("📦 My Orders", callback_data="my_orders"),
        InlineKeyboardButton("👤 My Profile", callback_data="my_profile"),
    )
    markup.add(InlineKeyboardButton("🎧 Customer Support", callback_data="support"))
    
    if user_id == ADMIN_ID:
        markup.add(InlineKeyboardButton("⚙️ Admin Control Panel", callback_data="admin_panel"))
    return markup

@bot.message_handler(commands=['start'])
def menu(message):
    user = message.from_user
    user_id_str = str(user.id)
    
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
        "╔══════════════════════╗\n"
        "   ⚡ **OFFICIAL GAMING ID STORE** ⚡\n"
        "╚══════════════════════╝\n\n"
        f"👋 Welcome, **{user.first_name}**!\n\n"
        "🌟 *Get premium Free Fire max IDs with instant verification & secure delivery.*\n\n"
        "🔹 🚀 Lightning Fast Service\n"
        "🔹 🛡️ 100% Secure & Trusted\n"
        f"🔹 💰 **Wallet Balance:** `₹{balance}`\n\n"
        "╔══════════════════════╗\n"
        "     👇 **CHOOSE AN OPTION BELOW** 👇\n"
        "╚══════════════════════╝"
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
            "╔══════════════════════╗\n"
            "         👤 **USER PROFILE INFO**\n"
            "╚══════════════════════╝\n\n"
            f"🆔 Telegram ID: `{user.id}`\n"
            f"👤 Name: {user.first_name}\n"
            f"💰 Wallet Balance: `₹{balance}`\n"
            f"📦 Total Orders: `{orders_count}`\n\n"
            "✨ *Thank you for being our valuable customer!*"
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("« Back to Main Menu", callback_data="main_menu"))
        bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "add_balance_menu":
        text = (
            "╔══════════════════════╗\n"
            "       💳 **ADD BALANCE / REDEEM**\n"
            "╚══════════════════════╝\n\n"
            "💡 To add funds to your wallet or for any redeem code queries, reach out directly to the owner:\n\n"
            "👉 Support Handle: **@Rahul_170_0**"
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("« Back to Main Menu", callback_data="main_menu"))
        bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "my_orders":
        orders = users_data[user_id_str]["orders"]
        if not orders:
            text = (
                "╔══════════════════════╗\n"
                "           📦 **MY ORDERS**\n"
                "╚══════════════════════╝\n\n"
                "❌ You haven't purchased any items yet."
            )
        else:
            text = (
                "╔══════════════════════╗\n"
                "       📦 **YOUR COMPLETED ORDERS**\n"
                "╚══════════════════════╝\n\n"
            )
            for idx, order in enumerate(orders, 1):
                text += f"🔸 {idx}. {order}\n"

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("« Back to Main Menu", callback_data="main_menu"))
        bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "buy_ff":
        stock = load_data(DATA_FILE)
        available_items = {k: v for k, v in stock.items() if v.get('status') == 'Available'}
        if not available_items:
            bot.answer_callback_query(call.id, "❌ Sorry, no IDs available right now!", show_alert=True)
            return

        markup = InlineKeyboardMarkup(row_width=1)
        for item_id, data in available_items.items():
            markup.add(InlineKeyboardButton(f"🔥 Lvl {data['level']} | UID {data['bundles']} | 💰 ₹{data['price']}", callback_data=f"buy_{item_id}"))
        markup.add(InlineKeyboardButton("« Back to Main Menu", callback_data="main_menu"))
        
        bot.edit_message_text("💎 **AVAILABLE FREE FIRE MAX IDS**\n\n✨ Click on any item below to proceed with your purchase:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data.startswith("buy_"):
        item_id = call.data.replace("buy_", "")
        stock = load_data(DATA_FILE)
        if item_id not in stock or stock[item_id].get('status') != 'Available':
            bot.answer_callback_query(call.id, "❌ This ID has already been sold or is unavailable!", show_alert=True)
            return

        item = stock[item_id]
        
        pending = load_data(PENDING_FILE)
        pending[user_id_str] = item_id
        save_data(PENDING_FILE, pending)

        pay_text = (
            "╔══════════════════════╗\n"
            "       🛒 **ID BOOKING DETAILS**\n"
            "╚══════════════════════╝\n\n"
            f"🔥 Level: `{item['level']}`\n"
            f"📦 Collection/UID: `{item['bundles']}`\n"
            f"💵 Price: `₹{item['price']}`\n\n"
            "📌 **How to Complete Purchase:**\n"
            f"1️⃣ Buy a Google Play Redeem Code worth `₹{item['price']}`.\n"
            "2️⃣ Paste and send your Redeem Code here in the chat!\n\n"
            "💡 *Example Format:*\n"
            "`ABCD1234EFGH5678`"
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("« Back to Catalog", callback_data="buy_ff"))
        bot.edit_message_text(pay_text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "admin_panel":
        if user.id != ADMIN_ID:
            return
        admin_text = (
            "╔══════════════════════╗\n"
            "     ⚙️ **ADMIN CONTROL PANEL**\n"
            "╚══════════════════════╝\n\n"
            "🔹 **To Add ID:**\n"
            "`/addff [Level] | [UID/Bundle] | [Price]`\n\n"
            "🔹 **To Add Balance:**\n"
            "`/addbalance [user_id] [amount]`\n\n"
            "🔹 **To Deliver ID:**\n"
            "`/deliverff [buyer_id] [item_id]`"
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("« Back to Main Menu", callback_data="main_menu"))
        bot.edit_message_text(admin_text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "support":
        text = (
            "╔══════════════════════╗\n"
            "     🎧 **CUSTOMER SUPPORT**\n"
            "╚══════════════════════╝\n\n"
            "💬 Need help with purchases, payments, or delivery? Contact us directly:\n\n"
            "👤 Owner & Support: **@Rahul_170_0**\n"
            "⏰ Availability: 24/7 Active"
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("« Back to Main Menu", callback_data="main_menu"))
        bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "main_menu":
        pending = load_data(PENDING_FILE)
        if user_id_str in pending:
            del pending[user_id_str]
            save_data(PENDING_FILE, pending)

        balance = users_data[user_id_str]["balance"]
        markup = get_main_menu_markup(user.id)
        text = (
            "╔══════════════════════╗\n"
            "   ⚡ **OFFICIAL GAMING ID STORE** ⚡\n"
            "╚══════════════════════╝\n\n"
            f"👋 Welcome back, **{user.first_name}**!\n\n"
            f"🔹 💰 **Wallet Balance:** `₹{balance}`\n\n"
            "╔══════════════════════╗\n"
            "     👇 **CHOOSE AN OPTION BELOW** 👇\n"
            "╚══════════════════════╝"
        )
        bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

# Handle user sending redeem code in chat
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

    del pending[str(user.id)]
    save_data(PENDING_FILE, pending)

    if item:
        item_desc = f"Level {item['level']} | UID {item['bundles']} (₹{item['price']})"
    else:
        item_desc = "Unknown Item"

    username = f"@{user.username}" if user.username else "No Username"

    admin_msg = (
        "╔══════════════════════╗\n"
        "   🔔 **NEW REDEEM CODE RECEIVED!**\n"
        "╚══════════════════════╝\n\n"
        f"👤 Buyer Name: {user.first_name}\n"
        f"🔗 Username: {username}\n"
        f"🆔 User ID: `{user.id}`\n"
        f"📦 Item Details: {item_desc}\n"
        f"🎟️ Redeem Code: `{redeem_code}`\n\n"
        "👉 Click the command below to deliver the ID:\n"
        f"`/deliverff {user.id} {item_id}`"
    )
    bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")
    bot.reply_to(message, "✅ Your redeem code has been successfully submitted to the admin! You will receive your ID after verification.")

# Admin command to add ID (/addff)
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
        bot.reply_to(message, "❌ Invalid format! Use:\n`/addff [Level] | [UID] | [Price]`", parse_mode="Markdown")

# Admin command to add balance (/addbalance)
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
        bot.reply_to(message, "❌ Invalid format! Use: `/addbalance [user_id] [amount]`", parse_mode="Markdown")

# Admin command to deliver ID (/deliverff)
@bot.message_handler(commands=['deliverff'])
def deliver_ff(message):
    if message.from_user.id != ADMIN_ID:
        return

    args = message.text.split()
    if len(args) < 3:
        bot.reply_to(message, "❌ Invalid format! Use: `/deliverff [buyer_id] [item_id]`", parse_mode="Markdown")
        return

    try:
        buyer_id = int(args[1])
        item_id = str(args[2])
    except ValueError:
        bot.reply_to(message, "❌ ID and User ID must be numbers!")
        return

    stock = load_data(DATA_FILE)
    if item_id not in stock or stock[item_id]['status'] == 'Sold':
        bot.reply_to(message, "❌ This ID does not exist or has already been sold!")
        return

    stock[item_id]['status'] = 'Sold'
    save_data(DATA_FILE, stock)

    item = stock[item_id]
    
    users_data = load_data(USERS_FILE)
    buyer_id_str = str(buyer_id)
    if buyer_id_str not in users_data:
        users_data[buyer_id_str] = {"balance": 0.0, "orders": []}
    
    order_info = f"Level {item['level']} | UID {item['bundles']} (₹{item['price']})"
    users_data[buyer_id_str]["orders"].append(order_info)
    save_data(USERS_FILE, users_data)

    try:
        bot.send_message(
            buyer_id,
            "╔══════════════════════╗\n"
            "   🎉 **DEAL SUCCESSFUL!** 🎉\n"
            "╚══════════════════════╝\n\n"
            f"🔥 Level: `{item['level']}`\n"
            f"📦 UID & Details: `{item['bundles']}`\n"
            f"💵 Price: `₹{item['price']}`\n\n"
            "✨ *Thank you for purchasing from our store! Enjoy your game!*"
        )
    except Exception as e:
        pass

    bot.reply_to(message, f"✅ ID successfully delivered to buyer (`{buyer_id}`)!", parse_mode="Markdown")

if __name__ == '__main__':
    keep_alive()
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)
    
    
    
                           
    
    
        
    
