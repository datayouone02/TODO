import datetime
from telebot import types
from settings import ADMIN_CHAT_ID, add_inline_cancel_button
from database import get_db_connection, user_data

def format_task_message(product_link, buyer_name, tags, additional_info, expiration_date):
    return (
        f"🔗 **Product Link**: {product_link}\n"
        f"👤 **Buyer's Name**: `{buyer_name}`\n"
        f"🏷️ **Tags**: {tags}\n"
        f"📝 **Additional Info**: {additional_info}\n"
        f"📅 **Expiration Date**: `{expiration_date}`"
    )

def create_task_keyboard(task_id):
    keyboard = types.InlineKeyboardMarkup()
    done_button = types.InlineKeyboardButton(text="✅ Done", callback_data=f"done_{task_id}")
    edit_button = types.InlineKeyboardButton(text="✍️ Edit", callback_data=f"edit_{task_id}")
    delete_button = types.InlineKeyboardButton(text="🗑️ Delete", callback_data=f"delete_{task_id}")
    keyboard.row(done_button, edit_button)
    keyboard.row(delete_button)
    return keyboard


def show_tasks_for_today(bot, message):
    chat_id = message.chat.id
    if chat_id != ADMIN_CHAT_ID:
        bot.send_message(chat_id, "🚫 Sorry, you are not authorized to use this bot.")
        return
    
    try:
        today_date = datetime.date.today().strftime('%Y-%m-%d')
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT rowid, product_link, buyer_name, tags, additional_info, expiration_date FROM tasks WHERE chat_id=? AND expiration_date=?", (chat_id, today_date))
            tasks = cursor.fetchall()

        if tasks:
            for task in tasks:
                task_id, product_link, buyer_name, tags, additional_info, expiration_date = task
                keyboard = create_task_keyboard(task_id)
                task_msg = format_task_message(product_link, buyer_name, tags, additional_info, expiration_date)
                bot.send_message(chat_id, task_msg, parse_mode='Markdown', reply_markup=keyboard)
        else:
            bot.send_message(chat_id, "📭 No tasks for today.")
    except Exception as e:
        bot.send_message(chat_id, "❌ An error occurred while fetching tasks. Please try again.")

def show_tasks_for_tomorrow(bot, message):
    chat_id = message.chat.id
    if chat_id != ADMIN_CHAT_ID:
        bot.send_message(chat_id, "🚫 Sorry, you are not authorized to use this bot.")
        return
    
    try:
        tomorrow_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT rowid, product_link, buyer_name, tags, additional_info, expiration_date FROM tasks WHERE chat_id=? AND expiration_date=?", (chat_id, tomorrow_date))
            tasks = cursor.fetchall()

        if tasks:
            for task in tasks:
                task_id, product_link, buyer_name, tags, additional_info, expiration_date = task
                keyboard = create_task_keyboard(task_id)
                task_msg = format_task_message(product_link, buyer_name, tags, additional_info, expiration_date)
                bot.send_message(chat_id, task_msg, parse_mode='Markdown', reply_markup=keyboard)
        else:
            bot.send_message(chat_id, "📭 No tasks for tomorrow.")
    except Exception as e:
        bot.send_message(chat_id, "❌ An error occurred while fetching tasks. Please try again.")

def show_tasks_by_day(bot, message):
    chat_id = message.chat.id
    if chat_id != ADMIN_CHAT_ID:
        bot.send_message(chat_id, "🚫 Sorry, you are not authorized to use this bot.")
        return
    msg = bot.send_message(chat_id, "📅 Enter the date (in YYYY-MM-DD format) ✍️:", reply_markup=add_inline_cancel_button())
    bot.register_next_step_handler(msg, lambda message: get_day_tasks(bot, message))

def get_day_tasks(bot, message):
    chat_id = message.chat.id
    if chat_id in user_data and 'cancelled' in user_data[chat_id]:
        del user_data[chat_id]
        return
    date_str = message.text.strip()
    try:
        year, month, day = map(int, date_str.split('-'))
        selected_date = datetime.date(year, month, day).strftime('%Y-%m-%d')

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT rowid, product_link, buyer_name, tags, additional_info, expiration_date FROM tasks WHERE chat_id=? AND expiration_date=?", (chat_id, selected_date))
            tasks = cursor.fetchall()

        if tasks:
            for task in tasks:
                task_id, product_link, buyer_name, tags, additional_info, expiration_date = task
                keyboard = create_task_keyboard(task_id)
                task_msg = format_task_message(product_link, buyer_name, tags, additional_info, expiration_date)
                bot.send_message(chat_id, task_msg, parse_mode='Markdown', reply_markup=keyboard)
        else:
            bot.send_message(chat_id, "📭 No tasks scheduled for the selected day.")
    except ValueError:
        bot.send_message(chat_id, "❌ Incorrect date format. Please enter it as YYYY-MM-DD (e.g., 2024-12-31).")

def search_tasks(bot, message):
    chat_id = message.chat.id
    if chat_id != ADMIN_CHAT_ID:
        bot.send_message(chat_id, "🚫 Sorry, you are not authorized to use this bot.")
        return
    msg = bot.send_message(chat_id, "🔍 Enter what you're searching for ✍️:", reply_markup=add_inline_cancel_button())
    bot.register_next_step_handler(msg, lambda message: perform_search(bot, message))

def perform_search(bot, message):
    chat_id = message.chat.id
    if chat_id in user_data and 'cancelled' in user_data[chat_id]:
        del user_data[chat_id]
        return
    search_query = message.text.strip()

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT rowid, product_link, buyer_name, tags, additional_info, expiration_date 
                FROM tasks 
                WHERE chat_id=? AND 
                (product_link LIKE ? OR buyer_name LIKE ? OR tags LIKE ? OR additional_info LIKE ?)
            """, (chat_id, f'%{search_query}%', f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'))
            tasks = cursor.fetchall()

        if tasks:
            for task in tasks:
                task_id, product_link, buyer_name, tags, additional_info, expiration_date = task
                keyboard = create_task_keyboard(task_id)
                task_msg = format_task_message(product_link, buyer_name, tags, additional_info, expiration_date)
                bot.send_message(chat_id, task_msg, parse_mode='Markdown', reply_markup=keyboard)
        else:
            bot.send_message(chat_id, "🔍 No tasks found matching your search.")
    except Exception as e:
        bot.send_message(chat_id, "❌ An error occurred while searching for tasks. Please try again.")

def show_missed_tasks(bot, message):
    chat_id = message.chat.id
    if chat_id != ADMIN_CHAT_ID:
        bot.send_message(chat_id, "🚫 Sorry, you are not authorized to use this bot.")
        return
    
    try:
        today_date = datetime.date.today().strftime('%Y-%m-%d')
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT rowid, product_link, buyer_name, tags, additional_info, expiration_date FROM tasks WHERE chat_id=? AND expiration_date<?", (chat_id, today_date))
            tasks = cursor.fetchall()

        if tasks:
            for task in tasks:
                task_id, product_link, buyer_name, tags, additional_info, expiration_date = task
                keyboard = create_task_keyboard(task_id)
                task_msg = format_task_message(product_link, buyer_name, tags, additional_info, expiration_date)
                bot.send_message(chat_id, task_msg, parse_mode='Markdown', reply_markup=keyboard)
        else:
            bot.send_message(chat_id, "📭 No missed tasks.")
    except Exception as e:
        bot.send_message(chat_id, "❌ An error occurred while fetching tasks. Please try again.")

def done_task(bot, callback_query):
    task_id_str = callback_query.data.split("_")[1]
    try:
        task_id = int(task_id_str)
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE rowid=?", (task_id,))
            conn.commit()
        bot.answer_callback_query(callback_query.id, text="✅ Task marked as done.")
        hide_done_button(bot, callback_query.message.chat.id, callback_query.message.message_id)
    except (ValueError, IndexError):
        bot.answer_callback_query(callback_query.id, text="❌ Error: Invalid task ID.", show_alert=True)
    except Exception as e:
        bot.answer_callback_query(callback_query.id, text="❌ An error occurred. Please try again.", show_alert=True)

def hide_done_button(bot, chat_id, message_id):
    keyboard = types.InlineKeyboardMarkup()
    bot.edit_message_reply_markup(chat_id, message_id, reply_markup=keyboard)

def edit_task(bot, callback_query):
    task_id_str = callback_query.data.split("_")[1]
    task_id = int(task_id_str)
    bot.answer_callback_query(callback_query.id, text="✍️ Edit Task")
    hide_done_button(bot, callback_query.message.chat.id, callback_query.message.message_id)
    
    keyboard = types.InlineKeyboardMarkup()
    link_button = types.InlineKeyboardButton("🔗 Edit Product Link", callback_data=f"editproductlink_{task_id}")
    keyboard.add(link_button)
    name_button = types.InlineKeyboardButton("👤 Edit Buyer's Name", callback_data=f"editbuyername_{task_id}")
    keyboard.add(name_button)
    date_button = types.InlineKeyboardButton("📅 Edit Expiration Date", callback_data=f"editexpirationdate_{task_id}")
    keyboard.add(date_button)
    cancel_button = types.InlineKeyboardButton("❌ Cancel", callback_data="cancel_")
    keyboard.add(cancel_button)
    
    bot.send_message(chat_id=callback_query.message.chat.id, text="🤔 Select the information you want to edit:", reply_markup=keyboard)

def edit_choice(bot, call):
    chat_id = call.message.chat.id
    if chat_id in user_data and 'cancelled' in user_data[chat_id]:
        del user_data[chat_id]
        return
    task_id_str = call.data.split("_")[1]
    task_id = int(task_id_str)
    data = call.data.split("_")
    keyboard = types.InlineKeyboardMarkup()
    cancel_button = types.InlineKeyboardButton("❌ Cancel", callback_data="cancel_")
    keyboard.add(cancel_button)
    if data[0] == "editexpirationdate":
        msg = bot.edit_message_text("📅 Enter the date (in YYYY-MM-DD format) ✍️:", chat_id=chat_id, message_id=call.message.message_id, reply_markup=keyboard)
        bot.register_next_step_handler(msg, lambda message: change_expiration_date(bot, message, task_id))
    elif data[0] == "editbuyername":
        msg = bot.edit_message_text("👤 Enter the buyer's name ✍️:", chat_id=chat_id, message_id=call.message.message_id, reply_markup=keyboard)
        bot.register_next_step_handler(msg, lambda message: change_buyer_name(bot, message, task_id))
    elif data[0] == "editproductlink":
        msg = bot.edit_message_text("🔗 Enter the product link ✍️:", chat_id=chat_id, message_id=call.message.message_id, reply_markup=keyboard)
        bot.register_next_step_handler(msg, lambda message: change_product_link(bot, message, task_id))

def change_buyer_name(bot, message, task_id):
    new_buyer_name = message.text.strip()
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET buyer_name=? WHERE rowid=?", (new_buyer_name, task_id))
        conn.commit()

    update_message(bot, message, task_id)

def change_product_link(bot, message, task_id):
    new_product_link = message.text.strip()
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET product_link=? WHERE rowid=?", (new_product_link, task_id))
        conn.commit()

    update_message(bot, message, task_id)

def change_expiration_date(bot, message, task_id):
    chat_id = message.chat.id
    new_date_str = message.text.strip()
    try:
        datetime.datetime.strptime(new_date_str, '%Y-%m-%d')
    except ValueError:
        bot.send_message(chat_id, "❌ Incorrect date format. Please enter it as YYYY-MM-DD (e.g., 2024-12-31).")
        return
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET expiration_date=? WHERE rowid=?", (new_date_str, task_id))
        conn.commit()

    update_message(bot, message, task_id)

def update_message(bot, message, task_id):
    chat_id = message.chat.id
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT rowid, product_link, buyer_name, tags, additional_info, expiration_date FROM tasks WHERE chat_id=? AND rowid=?", (chat_id, task_id))
        tasks = cursor.fetchall()

    if tasks:
        for task in tasks:
            task_id, product_link, buyer_name, tags, additional_info, expiration_date = task
            keyboard = create_task_keyboard(task_id)
            task_msg = (
                f"✅ **Updated successfully.**\n"
                f"🔗 **Product Link**: {product_link}\n"
                f"👤 **Buyer's Name**: `{buyer_name}`\n"
                f"🏷️ **Tags**: {tags}\n"
                f"📝 **Additional Info**: {additional_info}\n"
                f"📅 **Expiration Date**: `{expiration_date}`"
            )
            bot.send_message(chat_id, task_msg, parse_mode='Markdown', reply_markup=keyboard)

def show_stats(bot, message):
    chat_id = message.chat.id
    if chat_id != ADMIN_CHAT_ID:
        bot.send_message(chat_id, "🚫 Sorry, you are not authorized to use this bot.")
        return
    
    today_date = datetime.date.today().strftime('%Y-%m-%d')
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Total tasks
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE chat_id=?", (chat_id,))
        total_tasks = cursor.fetchone()[0]
        
        # Today's tasks
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE chat_id=? AND expiration_date=?", (chat_id, today_date))
        today_tasks = cursor.fetchone()[0]
        
        # Tomorrow's tasks
        tomorrow_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE chat_id=? AND expiration_date=?", (chat_id, tomorrow_date))
        tomorrow_tasks = cursor.fetchone()[0]
        
        # Missed tasks
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE chat_id=? AND expiration_date<?", (chat_id, today_date))
        missed_tasks = cursor.fetchone()[0]
        
        # Upcoming tasks (next 7 days)
        next_week = (datetime.date.today() + datetime.timedelta(days=7)).strftime('%Y-%m-%d')
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE chat_id=? AND expiration_date>? AND expiration_date<=?", 
                      (chat_id, today_date, next_week))
        upcoming_tasks = cursor.fetchone()[0]
    
    stats_msg = (
        f"📊 **Task Statistics**\n\n"
        f"📋 Total Tasks: `{total_tasks}`\n"
        f"📅 Today's Tasks: `{today_tasks}`\n"
        f"🌅 Tomorrow's Tasks: `{tomorrow_tasks}`\n"
        f"⏰ Missed Tasks: `{missed_tasks}`\n"
        f"📆 Next 7 Days: `{upcoming_tasks}`\n"
    )
    
    bot.send_message(chat_id, stats_msg, parse_mode='Markdown')

def delete_task(bot, callback_query):
    task_id_str = callback_query.data.split("_")[1]
    try:
        task_id = int(task_id_str)
        # Show confirmation dialog
        keyboard = types.InlineKeyboardMarkup()
        confirm_button = types.InlineKeyboardButton(text="✅ Yes, Delete", callback_data=f"confirmdelete_{task_id}")
        cancel_button = types.InlineKeyboardButton(text="❌ Cancel", callback_data="canceldelete")
        keyboard.row(confirm_button, cancel_button)
        
        bot.answer_callback_query(callback_query.id)
        bot.edit_message_reply_markup(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=keyboard
        )
        bot.send_message(
            callback_query.message.chat.id,
            "⚠️ Are you sure you want to delete this task? This action cannot be undone.",
            reply_markup=keyboard
        )
    except (ValueError, IndexError):
        bot.answer_callback_query(callback_query.id, text="❌ Error: Invalid task ID.", show_alert=True)

def confirm_delete_task(bot, callback_query):
    task_id_str = callback_query.data.split("_")[1]
    try:
        task_id = int(task_id_str)
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE rowid=?", (task_id,))
            conn.commit()
        
        bot.answer_callback_query(callback_query.id, text="🗑️ Task deleted successfully.")
        bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text="✅ Task has been deleted.",
            reply_markup=None
        )
    except (ValueError, IndexError):
        bot.answer_callback_query(callback_query.id, text="❌ Error: Invalid task ID.", show_alert=True)

def cancel_delete_task(bot, callback_query):
    bot.answer_callback_query(callback_query.id, text="❌ Deletion cancelled.")
    bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text="Operation cancelled.",
        reply_markup=None
    )

def show_all_tasks(bot, message):
    chat_id = message.chat.id
    if chat_id != ADMIN_CHAT_ID:
        bot.send_message(chat_id, "🚫 Sorry, you are not authorized to use this bot.")
        return
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT rowid, product_link, buyer_name, tags, additional_info, expiration_date 
                FROM tasks 
                WHERE chat_id=? 
                ORDER BY expiration_date ASC
            """, (chat_id,))
            tasks = cursor.fetchall()

        if tasks:
            bot.send_message(chat_id, f"📋 **All Tasks ({len(tasks)} total)**", parse_mode='Markdown')
            for task in tasks:
                task_id, product_link, buyer_name, tags, additional_info, expiration_date = task
                keyboard = create_task_keyboard(task_id)
                task_msg = format_task_message(product_link, buyer_name, tags, additional_info, expiration_date)
                bot.send_message(chat_id, task_msg, parse_mode='Markdown', reply_markup=keyboard)
        else:
            bot.send_message(chat_id, "📭 No tasks found.")
    except Exception as e:
        bot.send_message(chat_id, "❌ An error occurred while fetching tasks. Please try again.")
