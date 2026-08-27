from dotenv import load_dotenv
import os
from telebot import types

load_dotenv()

TOKEN = os.getenv('TOKEN')
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID'))
DATABASE = os.getenv('DATABASE')

def chunk_tags(tag_list, chunk_size):
    for i in range(0, len(tag_list), chunk_size):
        yield tag_list[i:i + chunk_size]

def add_inline_cancel_button():
    markup = types.InlineKeyboardMarkup()
    cancel_button = types.InlineKeyboardButton("❌ Cancel", callback_data="cancel_")
    markup.add(cancel_button)
    return markup