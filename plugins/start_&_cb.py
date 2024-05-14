import random
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, CallbackQuery
from helper.database import db
from config import Config, Txt
import humanize
from time import sleep


@Client.on_message(filters.private & filters.command("start"))
async def start(client, message):

    if message.from_user.id in Config.BANNED_USERS:
        await message.reply_text("Sorry, You are banned.")
        return

    user = message.from_user
    await db.add_user(client, message)
    button = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            '⛅ ᴜᴘᴅᴀᴛᴇ', url='https://t.me/Kdramaland'),
        InlineKeyboardButton(
            '🌨️ sᴜᴘᴘᴏʀᴛ', url='https://t.me/SnowDevs')
    ], [
        InlineKeyboardButton('❄️ ᴀʙᴏᴜᴛ', callback_data='about'),
        InlineKeyboardButton('❗ ʜᴇʟᴘ', callback_data='help')
    ], [InlineKeyboardButton('⚙️ sᴇʀᴠᴇʀ sᴛᴀᴛs', callback_data='stats')]])
    if Config.PICS:
        await message.reply_photo(random.choice(Config.PICS), caption=Txt.START_TXT.format(user.mention), reply_markup=button)
    else:
        await message.reply_text(text=Txt.START_TXT.format(user.mention), reply_markup=button, disable_web_page_preview=True)


@Client.on_message(filters.private & (filters.document | filters.audio | filters.video))
async def rename_start(client, message):
    file = getattr(message, message.media.value)
    filename = file.file_name
    filesize = humanize.naturalsize(file.file_size)
    
    if file.file_size > 2000 * 1024 * 1024:
        if not await db.is_user_bot_exist(Config.ADMIN[0]):
            return await message.reply_text("**⚠️ Sᴏʀʀy Bʀᴏ Tʜɪꜱ Bᴏᴛ Iꜱ Dᴏᴇꜱɴ'ᴛ Sᴜᴩᴩᴏʀᴛ Uᴩʟᴏᴀᴅɪɴɢ Fɪʟᴇꜱ Bɪɢɢᴇʀ Tʜᴀɴ 2Gʙ**")

    try:
        text = f"""**__What do you want me to do with this file.?__**\n\n**File Name** :- `{filename}`\n\n**File Size** :- `{filesize}`"""
        buttons = [[InlineKeyboardButton("📝 sᴛᴀʀᴛ ᴛᴏ ʀᴇɴᴀᴍᴇ 📝", callback_data="rename")],
                   [InlineKeyboardButton("✖️ ᴄᴀɴᴄᴇʟ ✖️", callback_data="close")]]
        await message.reply_text(text=text, reply_to_message_id=message.id, reply_markup=InlineKeyboardMarkup(buttons))
    except FloodWait as e:
        await sleep(e.value)
        text = f"""**__What do you want me to do with this file.?__**\n\n**File Name** :- `{filename}`\n\n**File Size** :- `{filesize}`"""
        buttons = [[InlineKeyboardButton("📝 sᴛᴀʀᴛ ᴛᴏ ʀᴇɴᴀᴍᴇ 📝", callback_data="rename")],
                   [InlineKeyboardButton("✖️ ᴄᴀɴᴄᴇʟ ✖️", callback_data="close")]]
        await message.reply_text(text=text, reply_to_message_id=message.id, reply_markup=InlineKeyboardMarkup(buttons))
    except:
        pass
