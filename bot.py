import telebot
import json
import os
from flask import Flask
from threading import Thread
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = "8497566219:AAHpCTLK_E360ak8GpliD7sVVZVYwRYF2mk"  # अपना बॉट टोकन यहाँ डालें
bot = telebot.TeleBot(API_TOKEN)
ADMIN_ID = 8380823727

DATA_FILE = 'ff_stock.json'
PENDING_FILE = 'pending_orders.json'

# डेटा लोड और सेव करने के लिए आसान फंक्शन्स (ताकि डेटा उड़े नहीं)
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

# Render के लिए Flask सर्वर
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

@bot.message_handler(commands=['start', 'menu'])
def menu(message):
    user_id = message.from_user.id
    pending = load_data(PENDING_FILE)
    if str(user_id) in pending:
        del pending[str(user_id)]
        save_data(PENDING_FILE, pending)

    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🔥 Buy Free Fire Max IDs", callback_data="buy_ff"),
        InlineKeyboardButton("💬 Customer Support", callback_data="support")
    )
    if user_id == ADMIN_ID:
        markup.add(InlineKeyboardButton("⚙️ Admin Panel (Add ID)", callback_data="admin_panel"))

    text = (
        "⚡ OFFICIAL GAMING ID STORE ⚡\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🎯 Trusted & 100% Secure Free Fire Max IDs Marketplace!\n\n"
        "💳 Payment Mode: Google Play Redeem Code\n"
        "👇 Select an option below to get started:"
    )
    bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    user = call.from_user
    stock = load_data(DATA_FILE)
    
    if call.data == "buy_ff":
        available_items = {k: v for k, v in stock.items() if v['status'] == 'Available'}
        
        if not available_items:
            bot.answer_callback_query(call.id, "⚠️ Sorry, no IDs are currently available in stock!", show_alert=True)
            return
            
        markup = InlineKeyboardMarkup(row_width=1)
        for item_id, data in available_items.items():
            markup.add(InlineKeyboardButton(f"🆔 Level {data['level']} | 📦 {data['bundles']} | 💰 ₹{data['price']}", callback_data=f"buy_{item_id}"))
        markup.add(InlineKeyboardButton("« Main Menu", callback_data="main_menu"))
        
        bot.edit_message_text(
            "💎 AVAILABLE FREE FIRE MAX IDS\n\n"
            "Click on any ID below to purchase:",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
        
    elif call.data.startswith("buy_"):
        item_id = call.data.replace("buy_", "")
        if item_id not in stock or stock[item_id]['status'] != 'Available':
            bot.answer_callback_query(call.id, "❌ This ID has already been sold!", show_alert=True)
            return
            
        item = stock[item_id]
        pending = load_data(PENDING_FILE)
        pending[str(user.id)] = item_id
        save_data(PENDING_FILE, pending)
        
        pay_text = (
            f"🛒 ID BOOKING DETAILS\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔥 Level: {item['level']}\n"
            f"📦 Collection: {item['bundles']}\n"
            f"💵 Price: ₹{item['price']}\n\n"
            f"📌 How to Purchase:\n"
            f"1️⃣ Purchase a Google Play Redeem Code worth ₹{item['price']}.\n"
            f"2️⃣ Now type and send your Google Play Redeem Code here in chat!\n\n"
            f"💡 Example Format:\n"
            f"ABCD1234EFGH5678"
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("« Back", callback_data="buy_ff"))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=pay_text, reply_markup=markup)

    elif call.data == "admin_panel":
        if user.id != ADMIN_ID:
            return
        admin_text = (
            "⚙️ ADMIN PANEL\n"
            "Use the following format to add a new ID:\n"
            "/addff [Level] | [Bundles] | [Price]\n\n"
            "Example:\n"
            "/addff 63 | UID 1772894853 | 1500"
        )
        bot.send_message(call.message.chat.id, admin_text)

    elif call.data == "main_menu":
        pending = load_data(PENDING_FILE)
        if str(user.id) in pending:
            del pending[str(user.id)]
            save_data(PENDING_FILE, pending)

        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("🔥 Buy Free Fire Max IDs", callback_data="buy_ff"),
            InlineKeyboardButton("💬 Customer Support", callback_data="support")
        )
        if user.id == ADMIN_ID:
            markup.add(InlineKeyboardButton("⚙️ Admin Panel (Add ID)", callback_data="admin_panel"))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="⚡ OFFICIAL GAMING ID STORE ⚡", reply_markup=markup)

    elif call.data == "support":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "💬 For support, contact: @Rahul_170_0")

@bot.message_handler(func=lambda message: not message.text.startswith('/'))
def handle_text_messages(message):
    user = message.from_user
    if user.id == ADMIN_ID:
        return  
        
    pending = load_data(PENDING_FILE)
    if str(user.id) not in pending:
        bot.reply_to(message, "⚠️ Please select an ID first from the menu by typing /menu or /start.")
        return  
        
    item_id = pending[str(user.id)]
    redeem_code = message.text.strip()
    
    stock = load_data(DATA_FILE)
    item = stock.get(item_id)
    
    del pending[str(user.id)]
    save_data(PENDING_FILE, pending)
    
    if item:
        item_desc = f"Level {item['level']} | {item['bundles']} | ₹{item['price']}"
    else:
        item_desc = "Unknown Item"
        
    username = f"@{user.username}" if user.username else "No Username"
    
    admin_msg = (
        f"🔔 NEW PAYMENT RECEIVED!\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 Buyer: {user.first_name}\n"
        f"🔗 Username: {username}\n"
        f"🆔 User ID: {user.id}\n"
        f"📦 Item Details: {item_desc}\n"
        f"🎟️ Redeem Code: {redeem_code}\n\n"
        f"👉 To deliver this ID, send command:\n"
        f"/deliverff {user.id} {item_id}"
    )
    bot.send_message(ADMIN_ID, admin_msg)
    bot.reply_to(message, "✅ Your redeem code has been successfully sent to the admin! You will receive the ID after verification.")

@bot.message_handler(commands=['addff'])
def add_ff(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        content = message.text.replace('/addff', '').strip()
        parts = content.split('|')
        level, bundles, price = parts[0].strip(), parts[1].strip(), float(parts[2].strip())
        
        stock = load_data(DATA_FILE)
        item_id = str(len(stock) + 1)
        # अगर आईडी पहले से मौजूद है तो नया यूनिक आईडी बनाएँ
        while item_id in stock:
            item_id = str(int(item_id) + 1)
            
        stock[item_id] = {
            "level": level,
            "bundles": bundles,
            "price": price,
            "status": "Available"
        }
        save_data(DATA_FILE, stock)
        
        bot.reply_to(message, f"✅ ID successfully added!\n🔥 Level: {level}\n💰 Price: ₹{price}")
    except Exception as e:
        bot.reply_to(message, "❌ Invalid format! Use this format:\n/addff 63 | UID 1772894853 | 1500")

@bot.message_handler(commands=['deliverff'])
def deliver_ff(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    args = message.text.split()
    if len(args) < 3:
        bot.reply_to(message, "❌ Correct format: /deliverff [User_ID] [Item_ID]")
        return

    try:
        buyer_id = int(args[1])
        item_id = str(args[2])
    except ValueError:
        bot.reply_to(message, "❌ Invalid User_ID or Item_ID format!")
        return

    stock = load_data(DATA_FILE)

    if item_id not in stock or stock[item_id]['status'] != 'Available':
        bot.reply_to(message, "❌ This ID is either sold or invalid!")
        return

    stock[item_id]['status'] = 'Sold'
    save_data(DATA_FILE, stock)

    item = stock[item_id]
    
    # यह लाइनें जोड़नी हैं ताकि पासवर्ड या डिटेल्स सही से उठकर आ जाए
    item_details = item.get('password', item.get('details', item.get('pass', item.get('bundles', 'Not Available'))))

    bot.send_message(
        buyer_id,
        f"🎉 CONGRATULATIONS! Deal Successful.\n"
        f"—————————————————\n"
        f"🔥 Level: {item.get('level', 'N/A')}\n"
        f"📦 ID & Password Details:\n{item_details}"
        )
    
    bot.reply_to(message, "✅ ID successfully delivered to the user!")
    

if __name__ == '__main__':
    keep_alive()
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)
                           
    
    
        
    

    
