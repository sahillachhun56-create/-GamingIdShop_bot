import telebot
import json
import os
import re
from flask import Flask
from threading import Thread
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# यहाँ अपना पूरा असली Telegram Bot Token डालें
API_TOKEN = "8497566219:AAF8YsfXyOlXm4YPELuvJBfNccwyMIp2gfw"
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
    markup.add(InlineKeyboardButton("🛡️ Direct Support", url="https://t.me/Rahul_170_0"))
    
    if user_id == ADMIN_ID:
        markup.add(InlineKeyboardButton("🔐 Admin Panel", callback_data="admin_panel"))
    return markup

@bot.message_handler(commands=['start'])
def menu(message):
    user = message.from_user
    user_id_str = str(user.id)
    
    users_data = load_data(USERS_FILE)
    if user_id_str not in users_data:
        users_data[user_id_str] = {"balance": 0.0, "orders": []}
        save_data(USERS_FILE, users_data)

    balance = users_data[user_id_str].get("balance", 0.0)
    markup = get_main_menu_markup(user.id)

    text = (
        "┏━━━ ⚡ **GAMING VAULT STORE** ⚡ ━━━┓\n"
        f"✦ **User:** `{user.first_name}`\n"
        f"✦ **Balance:** `₹{balance}`\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        "✨ *Instant Delivery & 100% Secure Trading Hub.*\n\n"
        "👇 **Select an option below:**"
    )
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")

# Admin command: /addff level | uid | price
@bot.message_handler(commands=['addff'])
def add_ff(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, f"❌ Unauthorized! Your ID (`{message.from_user.id}`) is not Admin.", parse_mode="Markdown")
        return
    try:
        content = message.text.replace('/addff', '').strip()
        parts = [p.strip() for p in content.split('|')]
        
        if len(parts) < 3:
            bot.reply_to(message, "❌ Format Error! Use:\n`/addff 63 | 1772894853 | 2000`", parse_mode="Markdown")
            return

        level = parts[0]
        bundles = parts[1]
        price = parts[2]

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
        
        success_text = (
            "┏━━━ ✅ **ID ADDED SUCCESSFULLY** ━━━┓\n"
            f"✦ **Index ID:** `{item_id}`\n"
            f"✦ **Level:** `{level}`\n"
            f"✦ **UID:** `{bundles}`\n"
            f"✦ **Price:** `₹{price}`\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"
        )
        bot.reply_to(message, success_text, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}\nUse format:\n`/addff 63 | 1772894853 | 2000`", parse_mode="Markdown")

# Admin command: /addbalance user_id amount
@bot.message_handler(commands=['addbalance'])
def add_balance_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, f"❌ Unauthorized! Your ID (`{message.from_user.id}`) is not Admin.", parse_mode="Markdown")
        return
    try:
        content = message.text.replace('/addbalance', '').strip()
        parts = content.split()
        
        if len(parts) < 2:
            bot.reply_to(message, "❌ Format Error! Use:\n`/addbalance user_id amount`", parse_mode="Markdown")
            return

        target_id = parts[0]
        amount = float(parts[1])
        
        users_data = load_data(USERS_FILE)
        if target_id not in users_data:
            users_data[target_id] = {"balance": 0.0, "orders": []}
        
        users_data[target_id]["balance"] += amount
        save_data(USERS_FILE, users_data)
        
        bot.reply_to(message, f"✅ Credited `₹{amount}` to user `{target_id}`.", parse_mode="Markdown")
        try:
            bot.send_message(int(target_id), f"🎉 Your wallet has been credited with `₹{amount}` by Admin!")
        except:
            pass
    except Exception as e:
        bot.reply_to(message, "❌ Format Error! Use: `/addbalance user_id amount`", parse_mode="Markdown")

# Admin command: /deliverff buyer_id item_id
@bot.message_handler(commands=['deliverff'])
def deliver_ff(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, f"❌ Unauthorized! Your ID (`{message.from_user.id}`) is not Admin.", parse_mode="Markdown")
        return

    content = message.text.replace('/deliverff', '').strip()
    args = content.split()
    if len(args) < 2:
        bot.reply_to(message, "❌ Format Error! Use: `/deliverff buyer_id item_id`", parse_mode="Markdown")
        return

    try:
        buyer_id = int(args[0])
        item_id = str(args[1])
    except ValueError:
        bot.reply_to(message, "❌ Error: IDs must be numbers!")
        return

    stock = load_data(DATA_FILE)
    if item_id not in stock or stock[item_id]['status'] == 'Sold':
        bot.reply_to(message, "❌ ID not found or already sold!", parse_mode="Markdown")
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
            "┏━━━ 🎉 **ORDER FULFILLED** ━━━┓\n"
            f"✦ **Level:** `{item['level']}`\n"
            f"✦ **UID/Details:** `{item['bundles']}`\n"
            f"✦ **Price:** `₹{item['price']}`\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            "✨ *Thank you for purchasing! Enjoy your game.*"
        )
    except Exception as e:
        pass

    bot.reply_to(message, f"✅ ID delivered successfully to buyer (`{buyer_id}`)!", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    user = call.from_user
    user_id_str = str(user.id)
    users_data = load_data(USERS_FILE)
    
    if user_id_str not in users_data:
        users_data[user_id_str] = {"balance": 0.0, "orders": []}
        save_data(USERS_FILE, users_data)

    try:
        if call.data == "my_profile":
            user_info = users_data.get(user_id_str, {"balance": 0.0, "orders": []})
            balance = user_info.get("balance", 0.0)
            orders_count = len(user_info.get("orders", []))
            
            safe_name = str(user.first_name).replace('*', '').replace('_', '').replace('`', '')
            username_str = f"@{user.username}" if user.username else "None"
            
            text = (
                "┏━━━ 👤 **OPERATOR PROFILE** ━━━┓\n"
                f"✦ **Name:** `{safe_name}`\n"
                f"✦ **Telegram ID:** `{user.id}`\n"
                f"✦ **Username:** `{username_str}`\n"
                f"✦ **Balance:** `₹{balance}`\n"
                f"✦ **Total Orders:** `{orders_count}`\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"
            )
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("« Back to Menu", callback_data="main_menu"))
            bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

        elif call.data == "add_balance_menu":
            balance = users_data[user_id_str].get("balance", 0.0)
            text = (
                "┏━━━ 💎 **WALLET & TOP-UP** ━━━┓\n\n"
                f"✦ **Current Balance:** `₹{balance}`\n\n"
                "To add funds or submit Google Play Redeem codes, contact the owner directly:\n\n"
                "💬 **Support:** [Click here to chat](https://t.me/Rahul_170_0)\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"
            )
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("💬 Open Direct Support", url="https://t.me/Rahul_170_0"))
            markup.add(InlineKeyboardButton("« Back to Menu", callback_data="main_menu"))
            bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown", disable_web_page_preview=True)

        elif call.data == "my_orders":
            orders = users_data[user_id_str].get("orders", [])
            if not orders:
                text = (
                    "┏━━━ 📦 **MY ORDERS** ━━━┓\n\n"
                    "❌ No purchase history found.\n"
                    "┗━━━━━━━━━━━━━━━━━━━━━━━┛"
                )
            else:
                text = "┏━━━ 📦 **YOUR ORDERS HISTORY** ━━━┓\n\n"
                for idx, order in enumerate(orders, 1):
                    text += f"🔹 {idx}. {order}\n"
                text += "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"

            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("« Back to Menu", callback_data="main_menu"))
            bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

        elif call.data == "buy_ff":
            stock = load_data(DATA_FILE)
            available_items = {k: v for k, v in stock.items() if v.get('status') == 'Available'}
            if not available_items:
                bot.answer_callback_query(call.id, "⚠️ No IDs available right now!", show_alert=True)
                return

            markup = InlineKeyboardMarkup(row_width=1)
            for item_id, data in available_items.items():
                markup.add(InlineKeyboardButton(f"⚡ Lvl {data['level']} | UID {data['bundles']} | ₹{data['price']}", callback_data=f"buy_{item_id}"))
            markup.add(InlineKeyboardButton("« Back to Menu", callback_data="main_menu"))
            
            bot.edit_message_text("┏━━━ 🛒 **AVAILABLE FREE FIRE IDS** ━━━┓\n\n✨ Select an ID below to buy:\n\n┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

        elif call.data.startswith("buy_"):
            item_id = call.data.replace("buy_", "")
            stock = load_data(DATA_FILE)
            if item_id not in stock or stock[item_id].get('status') == 'Sold':
                bot.answer_callback_query(call.id, "❌ Sorry, this ID is already sold!", show_alert=True)
                return

            item = stock[item_id]
            
            pending = load_data(PENDING_FILE)
            pending[user_id_str] = item_id
            save_data(PENDING_FILE, pending)

            pay_text = (
                "┏━━━ 🧾 **CHECKOUT DETAILS** ━━━┓\n"
                f"✦ **Level:** `{item['level']}`\n"
                f"✦ **UID/Details:** `{item['bundles']}`\n"
                f"✦ **Price:** `₹{item['price']}`\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                "📌 **How to Pay:**\n"
                f"1️⃣ Buy a Google Play Redeem Code of `₹{item['price']}`.\n"
                "2️⃣ Send the raw redeem code here in chat!\n\n"
                "💡 *Example:* `ABCD1234EFGH5678`"
            )
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("« Back to Catalog", callback_data="buy_ff"))
            bot.edit_message_text(pay_text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

        elif call.data == "admin_panel":
            if user.id != ADMIN_ID:
                return
            admin_text = (
                "┏━━━ 🔐 **ADMIN CONTROL PANEL** ━━━┓\n\n"
                "🔹 **Add ID:**\n`/addff 63 | 1772894853 | 2000`\n\n"
                "🔹 **Add Balance:**\n`/addbalance user_id amount`\n\n"
                "🔹 **Deliver ID:**\n`/deliverff buyer_id item_id`\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"
            )
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("« Back to Menu", callback_data="main_menu"))
            bot.edit_message_text(admin_text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

        elif call.data == "main_menu":
            pending = load_data(PENDING_FILE)
            if user_id_str in pending:
                del pending[user_id_str]
                save_data(PENDING_FILE, pending)

            balance = users_data[user_id_str].get("balance", 0.0)
            markup = get_main_menu_markup(user.id)
            text = (
                "┏━━━ ⚡ **GAMING VAULT STORE** ⚡ ━━━┓\n"
                f"✦ **User:** `{user.first_name}`\n"
                f"✦ **Balance:** `₹{balance}`\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                "✨ *Instant Delivery & 100% Secure Trading Hub.*\n\n"
                "👇 **Select an option below:**"
            )
            bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")
    except Exception as e:
        print(f"Callback Error: {e}")

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
        "┏━━━ 🚨 **NEW REDEEM CODE ORDER** ━━━┓\n"
        f"✦ **Buyer Name:** `{user.first_name}`\n"
        f"✦ **Username:** `{username}`\n"
        f"✦ **Telegram User ID:** `{user.id}`\n"
        f"✦ **Selected Item:** `{item_desc}`\n"
        f"✦ **Redeem Code:** `{redeem_code}`\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        "⚡ *Quick Deliver Command:*\n"
        f"`/deliverff {user.id} {item_id}`"
    )
    
    try:
        bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")
    except Exception as e:
        print(f"Error sending message to admin: {e}")
        
    bot.reply_to(message, "✅ Code submitted successfully! Admin will verify and deliver your ID soon.")

if __name__ == '__main__':
    keep_alive()
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)

    
    
                         
    
                                          

    


    
    
    
                           
    
    
        
    
