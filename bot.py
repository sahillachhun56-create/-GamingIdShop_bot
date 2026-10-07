import telebot
import json
import os
from flask import Flask
from threading import Thread
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = "8497566219:AAEpky5XxMTSU5E3vyqP6yuBmZrxmEJW9-g"  # Put your bot token here
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

# Premium Ultra-Modern UI Menu Layout
def get_main_menu_markup(user_id):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("⚡ Buy Free Fire IDs", callback_data="buy_ff"),
        InlineKeyboardButton("💎 Wallet & Topup", callback_data="add_balance_menu"),
    )
    markup.add(
        InlineKeyboardButton("📦 My Orders", callback_data="my_orders"),
        InlineKeyboardButton("👤 My Profile", callback_data="my_profile"),
    )
    markup.add(InlineKeyboardButton("🛡️ Direct Support", callback_data="support"))
    
    if user_id == ADMIN_ID:
        markup.add(InlineKeyboardButton("🔐 Admin Control Panel", callback_data="admin_panel"))
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
        "┏━━ 🌟 **GAMING VAULT STORE** 🌟 ━━┓\n"
        "┃  *The Ultimate Trading Hub*        ┃\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"✦ **Operator:** `{user.first_name}`\n"
        f"✦ **Status:** `ONLINE` 🟢\n"
        f"✦ **Wallet Funds:** `₹{balance}`\n\n"
        "╭━━━ 🚀 **SYSTEM FEATURES** ━━━╮\n"
        "┃ 🔹 Instant Key Auto-Delivery\n"
        "┃ 🔹 Verified & Secure Stock\n"
        "┃ 🔹 24/7 Priority Support\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
        "👇 *Select an operational mode below:*"
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
            "┏━━ 👤 **OPERATOR PROFILE** ━━┓\n\n"
            f"🔹 **Telegram ID:** `{user.id}`\n"
            f"🔹 **Username:** @{user.username if user.username else 'None'}\n"
            f"🔹 **Account Balance:** `₹{balance}`\n"
            f"🔹 **Total Acquisitions:** `{orders_count}`\n\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("« Return to Main Deck", callback_data="main_menu"))
        bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "add_balance_menu":
        text = (
            "┏━━ 💎 **FUNDS & TOP-UP** ━━┓\n\n"
            "✦ Want to add balance or submit a Google Play Redeem code? Connect securely with the core administrator:\n\n"
            "💬 **Support Channel:** `@Rahul_170_0`\n\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛"
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("« Return to Main Deck", callback_data="main_menu"))
        bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "my_orders":
        orders = users_data[user_id_str]["orders"]
        if not orders:
            text = (
                "┏━━ 📦 **ACQUISITION HISTORY** ━━┓\n\n"
                "⚠️ *No past records found in your archive.*\n\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛"
            )
        else:
            text = "┏━━ 📦 **YOUR VAULT RECORDS** ━━┓\n\n"
            for idx, order in enumerate(orders, 1):
                text += f"🔸 `[#{idx}]` {order}\n"
            text += "\n┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛"

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("« Return to Main Deck", callback_data="main_menu"))
        bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "buy_ff":
        stock = load_data(DATA_FILE)
        available_items = {k: v for k, v in stock.items() if v.get('status') == 'Available'}
        if not available_items:
            bot.answer_callback_query(call.id, "⚠️ Zero inventory detected! Check back later.", show_alert=True)
            return

        markup = InlineKeyboardMarkup(row_width=1)
        for item_id, data in available_items.items():
            markup.add(InlineKeyboardButton(f"⚡ Level {data['level']} | 🎯 UID {data['bundles']} | 💰 ₹{data['price']}", callback_data=f"buy_{item_id}"))
        markup.add(InlineKeyboardButton("« Return to Main Deck", callback_data="main_menu"))
        
        bot.edit_message_text("┏━━ 🛒 **LIVE INVENTORY CATALOG** ━━┓\n\n✨ Tap an item below to inspect and initiate secure checkout:\n\n┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data.startswith("buy_"):
        item_id = call.data.replace("buy_", "")
        stock = load_data(DATA_FILE)
        if item_id not in stock or stock[item_id].get('status') != 'Available':
            bot.answer_callback_query(call.id, "❌ Error: Item claimed or expired!", show_alert=True)
            return

        item = stock[item_id]
        
        pending = load_data(PENDING_FILE)
        pending[user_id_str] = item_id
        save_data(PENDING_FILE, pending)

        pay_text = (
            "┏━━ 🧾 **CHECKOUT PROTOCOL** ━━┓\n\n"
            f"🔥 **Level Specs:** `{item['level']}`\n"
            f"📦 **UID Collection:** `{item['bundles']}`\n"
            f"💵 **Total Cost:** `₹{item['price']}`\n\n"
            "╭━━━ ⚙️ **PAYMENT STEPS** ━━━╮\n"
            f"┃ 1️⃣ Purchase a Google Play Redeem Code worth `₹{item['price']}`.\n"
            "┃ 2️⃣ Type and send the raw code straight into this chat!\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
            "💡 *Example Code Format:*\n"
            "`ABCD1234EFGH5678`"
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("« Back to Catalog", callback_data="buy_ff"))
        bot.edit_message_text(pay_text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "admin_panel":
        if user.id != ADMIN_ID:
            return
        admin_text = (
            "┏━━ 🔐 **MASTER ADMIN DECK** ━━┓\n\n"
            "🔹 **Inject New ID Stock:**\n"
            "`/addff [Level] | [UID] | [Price]`\n\n"
            "🔹 **Top-up User Wallet:**\n"
            "`/addbalance [user_id] [amount]`\n\n"
            "🔹 **Dispatch Order to Client:**\n"
            "`/deliverff [buyer_id] [item_id]`\n\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛"
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("« Return to Main Deck", callback_data="main_menu"))
        bot.edit_message_text(admin_text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "support":
        text = (
            "┏━━ 🛡️ **CUSTOMER ASSISTANCE** ━━┓\n\n"
            "✦ Facing trouble with codes, deliveries, or payments? Connect instantly with high-priority support:\n\n"
            "👤 **Lead Administrator:** `@Rahul_170_0`\n"
            "⏰ **Active Hours:** `24/7 Online`\n\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛"
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("« Return to Main Deck", callback_data="main_menu"))
        bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "main_menu":
        pending = load_data(PENDING_FILE)
        if user_id_str in pending:
            del pending[user_id_str]
            save_data(PENDING_FILE, pending)

        balance = users_data[user_id_str]["balance"]
        markup = get_main_menu_markup(user.id)
        text = (
            "┏━━ 🌟 **GAMING VAULT STORE** 🌟 ━━┓\n"
            "┃  *The Ultimate Trading Hub*        ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            f"✦ **Operator:** `{user.first_name}`\n"
            f"✦ **Wallet Funds:** `₹{balance}`\n\n"
            "👇 *Select an operational mode below:*"
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
        "┏━━ 🚨 **NEW TRANSACTION ALERT** ━━┓\n\n"
        f"👤 **Buyer Name:** {user.first_name}\n"
        f"🔗 **Username:** {username}\n"
        f"🆔 **User ID:** `{user.id}`\n"
        f"📦 **Item Selected:** {item_desc}\n"
        f"🎟️ **Redeem Code:** `{redeem_code}`\n\n"
        "⚡ **Quick Action Command:**\n"
        f"`/deliverff {user.id} {item_id}`\n\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛"
    )
    bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")
    bot.reply_to(message, "✅ **Code Transmitted!** Your redeem code has been securely routed to the admin. Verification and delivery are underway.")

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
        bot.reply_to(message, f"✅ **Success!** ID registered with index ID: `{item_id}`", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, "❌ **Format Error!** Use layout:\n`/addff [Level] | [UID] | [Price]`", parse_mode="Markdown")

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
        
        bot.reply_to(message, f"✅ Successfully credited `₹{amount}` to user `{target_id}`.", parse_mode="Markdown")
        bot.send_message(int(target_id), f"🎉 **Wallet Update:** Your account has been credited with `₹{amount}` by Admin!")
    except Exception as e:
        bot.reply_to(message, "❌ **Format Error!** Use: `/addbalance [user_id] [amount]`", parse_mode="Markdown")

# Admin command to deliver ID (/deliverff)
@bot.message_handler(commands=['deliverff'])
def deliver_ff(message):
    if message.from_user.id != ADMIN_ID:
        return

    args = message.text.split()
    if len(args) < 3:
        bot.reply_to(message, "❌ **Format Error!** Use: `/deliverff [buyer_id] [item_id]`", parse_mode="Markdown")
        return

    try:
        buyer_id = int(args[1])
        item_id = str(args[2])
    except ValueError:
        bot.reply_to(message, "❌ **Error:** ID and User ID must be numeric digits!")
        return

    stock = load_data(DATA_FILE)
    if item_id not in stock or stock[item_id]['status'] == 'Sold':
        bot.reply_to(message, "❌ **Error:** Asset not found or already dispatched!")
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
            "┏━━ 🎉 **ORDER FULFILLED** 🎉 ━━┓\n\n"
            f"🔥 **Level:** `{item['level']}`\n"
            f"📦 **UID / Details:** `{item['bundles']}`\n"
            f"💵 **Price:** `₹{item['price']}`\n\n"
            "✨ *Thank you for trading with us! Enjoy your gaming experience.*"
        )
    except Exception as e:
        pass

    bot.reply_to(message, f"✅ Asset successfully dispatched to client (`{buyer_id}`)!", parse_mode="Markdown")

if __name__ == '__main__':
    keep_alive()
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)

    
    
    
                           
    
    
        
    
