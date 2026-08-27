import telebot
from telebot import types
from settings import ADMIN_CHAT_ID, chunk_tags, add_inline_cancel_button
from database import user_data, get_db_connection
import datetime

tag_options = [
    "Netflix", "Extra", "Cookies", "Crack", "Officiel", "VPN", "Isra", "Asma", "Page", "Asma Bl", "Eleven", "King",
    "1 month", "2 month", "3 month", "6 month", "1 year", "2 year", "1 screen", "2 screen", "3 screen", "4 screen", "5 screen", 
    "Flexy", "BaridiMob", "CCP", "Prime Video", "Osn+", "Shahid Vip", "Spotify", "Crunchyroll"
]

def add_task(bot, message):
    chat_id = message.chat.id
    if chat_id != ADMIN_CHAT_ID:
        bot.send_message(chat_id, "🚫 Sorry, you are not authorized to use this bot.")
        return
    user_data[chat_id] = {}
    msg = bot.send_message(chat_id, "✍️ Enter the product link:", reply_markup=add_inline_cancel_button())
    bot.register_next_step_handler(msg, lambda message: save_product_link(bot, message))

def save_product_link(bot, message):
    chat_id = message.chat.id
    product_link = message.text.strip()
    if chat_id in user_data and 'cancelled' in user_data[chat_id]:
        del user_data[chat_id]
        return
    if product_link:
        user_data[chat_id]["product_link"] = product_link
        msg = bot.send_message(chat_id, "✍️ Enter the buyer's name:", reply_markup=add_inline_cancel_button())
        bot.register_next_step_handler(msg, lambda message: save_buyer_name(bot, message))
    else:
        bot.send_message(chat_id, "⚠️ Product link cannot be empty. Please enter the product link again.")

def save_buyer_name(bot, message):
    chat_id = message.chat.id
    if chat_id in user_data and 'cancelled' in user_data[chat_id]:
        del user_data[chat_id]
        return
    buyer_name = message.text.strip()
    if buyer_name:
        user_data[chat_id]["buyer_name"] = buyer_name
        ask_for_tags(bot, message)
    else:
        bot.send_message(chat_id, "⚠️ Buyer's name cannot be empty. Please enter the buyer's name again.")

def handle_tag_selection(bot, call):
    chat_id = call.message.chat.id
    data = call.data.split("_")
    if data[0] == 'tag':
        selected_tag = data[1]
        page = int(data[2])
        
        if "tags" not in user_data[chat_id]:
            user_data[chat_id]["tags"] = []
        if selected_tag not in user_data[chat_id]["tags"]:
            user_data[chat_id]["tags"].append(selected_tag)
            
        ask_for_tags(bot, call.message, page=page)

    elif data[0] == 'more':
        page = int(data[1])
        ask_for_tags(bot, call.message, page=page)
    elif data[0] == 'back':
        page = int(data[1])
        ask_for_tags(bot, call.message, page=page)

def ask_for_tags(bot, message, page=0):
    chat_id = message.chat.id
    remaining_tags = [tag for tag in tag_options if tag not in user_data[chat_id].get("tags", [])]

    chunked_tags = list(chunk_tags(remaining_tags, 7))
    current_tags = chunked_tags[page] if page < len(chunked_tags) else []

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for tag in current_tags:
        keyboard.add(types.InlineKeyboardButton(text=tag, callback_data=f"tag_{tag}_{page}"))

    back_page = len(chunked_tags) - 1 if page == 0 else page - 1
    back_button = types.InlineKeyboardButton(text="⏪", callback_data=f"back_{back_page}")
    
    more_page = 0 if page == len(chunked_tags) - 1 else page + 1
    more_button = types.InlineKeyboardButton(text="⏩", callback_data=f"more_{more_page}")
    
    keyboard.row(back_button, more_button)

    keyboard.add(types.InlineKeyboardButton(text="👉 Continue", callback_data="continue_with_tags"))
    cancel_button = types.InlineKeyboardButton("❌ Cancel", callback_data="cancel_")
    keyboard.add(cancel_button)

    try:
        bot.edit_message_text("📋 Add your important info:", chat_id=chat_id, message_id=message.message_id, reply_markup=keyboard)
    except telebot.apihelper.ApiTelegramException:
        bot.send_message(chat_id, "📋 Add your important info:", reply_markup=keyboard)

def ask_for_additional_info(bot, message):
    chat_id = message.chat.id
    keyboard = types.InlineKeyboardMarkup()
    yes_button = types.InlineKeyboardButton(text="▶️ Yes", callback_data="additional_info_yes")
    no_button = types.InlineKeyboardButton(text="⏸️ No", callback_data="additional_info_no")
    cancel_button = types.InlineKeyboardButton("❌ Cancel", callback_data="cancel_")
    keyboard.row(yes_button, no_button)
    keyboard.add(cancel_button)
    try:
        bot.edit_message_text("💬 Any additional information to add?", chat_id=chat_id, message_id=message.message_id, reply_markup=keyboard)
    except telebot.apihelper.ApiTelegramException:
        msg = bot.send_message(chat_id, "💬 Any additional information to add?", reply_markup=keyboard)

def additional_info_response(bot, call):
    chat_id = call.message.chat.id
    if call.data == "additional_info_yes":
        keyboard = types.InlineKeyboardMarkup()
        cancel_button = types.InlineKeyboardButton("❌ Cancel", callback_data="cancel_")
        keyboard.add(cancel_button)
        msg = bot.edit_message_text("✍️ Please enter the additional information:", chat_id, call.message.message_id, reply_markup=keyboard)
        bot.register_next_step_handler(msg, lambda message: save_additional_info(bot, message))
    elif call.data == "additional_info_no":
        ask_for_expiration_date(bot, call.message)

def save_additional_info(bot, message):
    chat_id = message.chat.id
    if chat_id in user_data and 'cancelled' in user_data[chat_id]:
        del user_data[chat_id]
        return
    additional_info = message.text.strip()
    user_data[chat_id]["additional_info"] = additional_info
    ask_for_expiration_date(bot, message)

def ask_for_expiration_date(bot, message):
    chat_id = message.chat.id
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    options = ["1 month", "2 months", "3 months", "6 months", "1 year", "✍️ Enter manually"]
    for opt in options:
        keyboard.add(types.InlineKeyboardButton(text=opt, callback_data=f"expiry_{opt.replace(' ', '_')}"))
    cancel_button = types.InlineKeyboardButton("❌ Cancel", callback_data="cancel_")
    keyboard.add(cancel_button)
    try:
        bot.edit_message_text("📅 Choose the subscription expiry period or enter manually:", chat_id=chat_id, message_id=message.message_id, reply_markup=keyboard)
    except telebot.apihelper.ApiTelegramException:
        msg = bot.send_message(chat_id, "📅 Choose the subscription expiry period or enter manually:", reply_markup=keyboard)

def expiry_selection(bot, call):
    chat_id = call.message.chat.id
    option = call.data[len('expiry_'):].replace('_', ' ')

    today = datetime.date.today()

    if option == "✍️ Enter manually":
        bot.edit_message_text("📅 Enter the expiration date (in YYYY-MM-DD format) ✍️:", chat_id, call.message.message_id)
        bot.register_next_step_handler_by_chat_id(chat_id, lambda message: save_manual_expiry_date(bot, message))
    else:
        periods = {"1 month": 1, "2 months": 2, "3 months": 3, "6 months": 6, "1 year": 12}
        months_to_add = periods.get(option, None)

        if months_to_add is not None:
            bot.delete_message(chat_id, call.message.message_id)
            expiry_date = add_months(today, months_to_add)
            expiry_date_str = expiry_date.strftime('%Y-%m-%d')
            user_data[chat_id]["expiration_date"] = expiry_date_str
            save_task_date_after_selection(bot, call.message)
        else:
            bot.send_message(chat_id, "❌ An error occurred, please try again.")

def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, [31, 29 if year % 4 == 0 and not year % 100 == 0 or year % 400 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
    return datetime.date(year, month, day)

def save_manual_expiry_date(bot, message):
    chat_id = message.chat.id
    if chat_id in user_data and 'cancelled' in user_data[chat_id]:
        del user_data[chat_id]
        return
    try:
        expiration_date = datetime.datetime.strptime(message.text.strip(), '%Y-%m-%d').date()
        
        # Validate that the date is not in the past
        if expiration_date < datetime.date.today():
            bot.send_message(chat_id, "⚠️ The expiration date cannot be in the past. Please enter a valid date (YYYY-MM-DD):")
            bot.register_next_step_handler(message, lambda msg: save_manual_expiry_date(bot, msg))
            return
            
        user_data[chat_id]["expiration_date"] = expiration_date.strftime('%Y-%m-%d')
        save_task_date_after_selection(bot, message)
    except ValueError:
        bot.send_message(chat_id, "❌ Incorrect date format. Please enter it as YYYY-MM-DD ✍️ (e.g., 2024-12-31):")
        bot.register_next_step_handler(message, lambda msg: save_manual_expiry_date(bot, msg))
        return

def save_task_date_after_selection(bot, message):
    chat_id = message.chat.id
    expiration_date_str = user_data[chat_id].get("expiration_date", "")
    if expiration_date_str:
        product_link = user_data[chat_id].get("product_link", "")
        buyer_name = user_data[chat_id].get("buyer_name", "")
        additional_info = user_data[chat_id].get("additional_info", "N/A")
        tags_str = " / ".join(user_data[chat_id].get("tags", [])) or "No tags"

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO tasks (chat_id, product_link, buyer_name, tags, additional_info, expiration_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (chat_id, product_link, buyer_name, tags_str, additional_info, expiration_date_str))
                conn.commit()

            success_message = (
                    f"📥 **Task added successfully!**\n"
                    f"🔗 **Product Link**: {product_link}\n"
                    f"👤 **Buyer's Name**: `{buyer_name}`\n"
                    f"🏷️ **Tags**: {tags_str}\n"
                    f"📝 **Additional Info**: {additional_info}\n"
                    f"📅 **Expiration Date**: `{expiration_date_str}`"
                )
            try:
                last_message_id = user_data[chat_id].get("last_message_id")
                bot.edit_message_text(success_message, chat_id=chat_id, message_id=last_message_id, parse_mode='Markdown')
            except Exception:
                bot.send_message(chat_id, success_message, parse_mode='Markdown')

            del user_data[chat_id]
        except Exception as e:
            error_message = "❌ Error: Failed to save the task. Please try again."
            try:
                last_message_id = user_data[chat_id].get("last_message_id")
                bot.edit_message_text(error_message, chat_id=chat_id, message_id=last_message_id)
            except Exception:
                bot.send_message(chat_id, error_message)
    else:
        error_message = "❌ Error: No expiration date selected."
        try:
            last_message_id = user_data[chat_id].get("last_message_id")
            bot.edit_message_text(error_message, chat_id=chat_id, message_id=last_message_id)
        except Exception:
            bot.send_message(chat_id, error_message)
