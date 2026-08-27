import telebot
from settings import TOKEN, DATABASE, ADMIN_CHAT_ID
from database import user_data
from add_task import add_task, handle_tag_selection, ask_for_additional_info, additional_info_response, expiry_selection
from services import (show_tasks_for_today, show_tasks_by_day, search_tasks, done_task, edit_task, 
                     edit_choice, show_missed_tasks, show_tasks_for_tomorrow, show_stats, 
                     delete_task, confirm_delete_task, cancel_delete_task, show_all_tasks)

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['get_db'])
def send_database(message):
    chat_id = message.chat.id
    if chat_id == ADMIN_CHAT_ID:
        db_path = DATABASE
        with open(db_path, 'rb') as db_file:
            bot.send_document(chat_id, db_file)
    else:
        bot.send_message(chat_id, "Sorry, you are not authorized to use this bot.")

@bot.message_handler(commands=['get_id'])
def send_chat_id(message):
    chat_id = message.chat.id
    bot.reply_to(message, f"Your chat ID is: {chat_id}")

@bot.message_handler(commands=['start'])
def start_command(message):
    chat_id = message.chat.id
    if chat_id != ADMIN_CHAT_ID:
        bot.send_message(chat_id, "🚫 Sorry, you are not authorized to use this bot.")
        return
    welcome_msg = (
        "👋 **Welcome to your TODO Bot!**\n\n"
        "I'll help you manage your tasks efficiently.\n"
        "Use /help to see all available commands."
    )
    bot.send_message(chat_id, welcome_msg, parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def help_command(message):
    chat_id = message.chat.id
    if chat_id != ADMIN_CHAT_ID:
        bot.send_message(chat_id, "🚫 Sorry, you are not authorized to use this bot.")
        return
    help_text = (
        "📖 **Available Commands:**\n\n"
        "➕ `/add` - Add a new task\n"
        "📋 `/show_all` - View all tasks\n"
        "📅 `/show_today` - View today's tasks\n"
        "🌅 `/show_tomorrow` - View tomorrow's tasks\n"
        "📆 `/show_by_day` - View tasks for a specific date\n"
        "⏰ `/show_missed` - View overdue tasks\n"
        "🔍 `/search` - Search for tasks\n"
        "📊 `/stats` - View task statistics\n"
        "🆔 `/get_id` - Get your chat ID\n"
        "💾 `/get_db` - Download database (admin only)\n"
        "❓ `/help` - Show this help message\n\n"
        "**Tip:** You can mark tasks as done, edit, or delete them using the buttons!"
    )
    bot.send_message(chat_id, help_text, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "cancel_")
def handle_cancel(callback_query):
    chat_id = callback_query.from_user.id
    user_data[chat_id] = {'cancelled': True}
    bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text="You have canceled the operation.", reply_markup=None)

@bot.message_handler(commands=['add'])
def add_task_callback_query(message):
    add_task(bot, message)

@bot.callback_query_handler(func=lambda call: call.data.startswith('tag_') or call.data.startswith('more_') or call.data.startswith('back_'))
def handle_tag_selection_callback_query(call):
    handle_tag_selection(bot, call)

@bot.callback_query_handler(func=lambda call: call.data == "continue_with_tags")
def continue_after_tags_callback_query(call):
    ask_for_additional_info(bot, call.message)

@bot.callback_query_handler(func=lambda call: call.data in ["additional_info_yes", "additional_info_no"])
def handle_additional_info_response_callback_query(call):
    additional_info_response(bot, call)

@bot.callback_query_handler(func=lambda call: call.data.startswith('expiry_'))
def handle_expiry_selection_callback_query(call):
    expiry_selection(bot, call)

@bot.message_handler(commands=['show_today'])
def show_tasks_for_today_callback_query(message):
    show_tasks_for_today(bot, message)

@bot.message_handler(commands=['show_by_day'])
def show_tasks_by_day_callback_query(message):
    show_tasks_by_day(bot, message)

@bot.message_handler(commands=['search'])
def search_tasks_callback_query(message):
    search_tasks(bot, message)

@bot.message_handler(commands=['show_missed'])
def show_missed_tasks_callback_query(message):
    show_missed_tasks(bot, message)

@bot.message_handler(commands=['show_tomorrow'])
def show_tasks_for_tomorrow_callback_query(message):
    show_tasks_for_tomorrow(bot, message)

@bot.message_handler(commands=['stats'])
def show_stats_callback_query(message):
    show_stats(bot, message)

@bot.message_handler(commands=['show_all'])
def show_all_tasks_callback_query(message):
    show_all_tasks(bot, message)

@bot.callback_query_handler(func=lambda call: call.data.startswith('done_'))
def handle_done_task(callback_query):
    done_task(bot, callback_query)

@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_'))
def handle_edit_task(callback_query):
    edit_task(bot, callback_query)

@bot.callback_query_handler(func=lambda call: call.data.startswith('editproductlink_') or call.data.startswith('editbuyername_') or call.data.startswith('editexpirationdate_'))
def edit_choice_callback_query(call):
    edit_choice(bot, call)

@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_'))
def handle_delete_task(callback_query):
    delete_task(bot, callback_query)

@bot.callback_query_handler(func=lambda call: call.data.startswith('confirmdelete_'))
def handle_confirm_delete_task(callback_query):
    confirm_delete_task(bot, callback_query)

@bot.callback_query_handler(func=lambda call: call.data == 'canceldelete')
def handle_cancel_delete_task(callback_query):
    cancel_delete_task(bot, callback_query)

if __name__ == '__main__':
    bot.infinity_polling()