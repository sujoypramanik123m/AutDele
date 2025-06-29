import random
import logging
from pyrogram import Client, filters, enums
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait, ChatAdminRequired, UserNotParticipant, PeerIdInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, CallbackQuery, Message
from .database import db
from config import Config, Txt
from info import AUTH_CHANNEL
from helper.utils import is_req_subscribed
import humanize
from time import sleep

logger = logging.getLogger(__name__)

@Client.on_message(filters.private & filters.command("start"))
async def start(client, message):

    if message.from_user.id in Config.BANNED_USERS:
        await message.reply_text("Sorry, You are banned.")
        return

    user = message.from_user
    await db.add_user(user.id)
    button = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            'ᴜᴘᴅᴀᴛᴇꜱ', url='https://t.me/Bot_Cracker'),
        InlineKeyboardButton(
            'ꜱᴜᴘᴘᴏʀᴛ', url='https://t.me/+O1mwQijo79s2MjJl')],
        [InlineKeyboardButton('ᴏᴡɴᴇʀ', user_id=1733124290)
    ], [
        InlineKeyboardButton('ʙᴏᴛꜱ', url='https://t.me/Bot_Cracker/17'),
        InlineKeyboardButton('ᴜᴩᴅᴀᴛᴇꜱ', url='https://t.me/Mod_Moviez_X')]])
    if Config.PICS:
        await message.reply_photo(random.choice(Config.PICS), caption=Txt.START_TXT.format(user.mention), reply_markup=button)
    else:
        await message.reply_text(text=Txt.START_TXT.format(user.mention), reply_markup=button, disable_web_page_preview=True)



@Client.on_message(filters.group & ~filters.service)
async def delete_message(bot: Client, message: Message):
    if (
       user.status != enums.ChatMemberStatus.ADMINISTRATOR
       and user.status != enums.ChatMemberStatus.OWNER
       and user_id not in Config.ADMIN
        ):
       return
    text = message.text.lower()
    words = text.split()
    for word in words:
        if word.startswith("http") or (word.startswith("@") or (word.startswith("t.me/") or (word.startswith("bitly") and word != "@admin"):
            
        try:
            await message.delete()
        except:
            pass
