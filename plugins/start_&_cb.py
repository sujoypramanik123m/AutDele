import random
import logging
from pyrogram import Client, filters, enums
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait, ChatAdminRequired
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, CallbackQuery
from helper.database import db
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
    await db.add_user(client, message)
    button = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            '⛅ Uᴘᴅᴀᴛᴇꜱ', url='https://t.me/Bot_Cracker'),
        InlineKeyboardButton(
            ' Sᴜᴘᴘᴏʀᴛ 🌨️', url='https://t.me/+O1mwQijo79s2MjJl')
    ], [
        InlineKeyboardButton('❄️ Δʙᴏᴜᴛ', callback_data='about'),
        InlineKeyboardButton('βᴏᴛꜱ ⚧️', url='https://t.me/Bot_Cracker/17'),
        InlineKeyboardButton(' Hᴇʟᴩ ❗', callback_data='help')
    ], [InlineKeyboardButton('⚙️ sᴛΔᴛs ⚙️', callback_data='stats')]])
    if Config.PICS:
        await message.reply_photo(random.choice(Config.PICS), caption=Txt.START_TXT.format(user.mention), reply_markup=button)
    else:
        await message.reply_text(text=Txt.START_TXT.format(user.mention), reply_markup=button, disable_web_page_preview=True)
        
@Client.on_message(filters.private & filters.command("season"))
async def sydson(client, message):
    mrsyd = await db.get_sydson(message.from_user.id)
    if mrsyd == "True":
        button = InlineKeyboardMarkup([[
          InlineKeyboardButton('Fᴀʟꜱᴇ ✖️', callback_data='season_false')
          ],[
          InlineKeyboardButton("✖️ Close", callback_data="close")
        ]])
    else:
        button = InlineKeyboardMarkup([[
          InlineKeyboardButton('Tʀᴜᴇ ✅', callback_data='season_true')
          ],[
          InlineKeyboardButton("✖️ Close", callback_data="close")
        ]])
    await message.reply_text(text="Sᴇᴛ ᴛʀᴜᴇ ᴏʀ ꜰᴀʟꜱᴇ, ɪꜰ ꜱᴇᴀꜱᴏɴ ɴᴜᴍʙᴇʀ ɪꜱ ᴛᴏ ʙᴇ ɪɴ ꜰɪʟᴇ ᴇᴠᴇʀʏᴛɪᴍᴇ (ɪꜰ ꜰɪʟᴇ ᴅᴏɴᴛ ʜᴀᴠᴇ ꜱᴇᴀꜱᴏɴ ɴᴏ. ɪᴛ ᴡɪʟʟ ʙᴇ ᴅᴇꜰᴜᴀʟᴛ ᴛᴏ 1) ᴏʀ ꜰᴀʟꜱᴇ ᴛᴏ ᴀᴠᴏɪᴅ ꜱᴇᴀꜱᴏɴ ᴛᴀɢ", reply_markup=button)   


@Client.on_message(filters.private & (filters.document | filters.video))
async def handle_ile(client, message):
    user_id = message.from_user.id
    username = message.from_user.mention

    file_id = message.document.file_id if message.document else message.video.file_id
    file_name = message.document.file_name if message.document else message.video.file_name


    log_msg = await client.send_cached_media(chat_id=Config.LOG_CHANNEL, file_id=file_id)

    # 4. Generate stream/download URLs
    
 


    # 6. Send Link Buttons
    buttons = [
        [InlineKeyboardButton("Sᴀᴍᴩʟᴇ - 30ꜱ", callback_data="sample")],
        [InlineKeyboardButton("Gᴇɴᴇʀᴀᴛᴇ Sᴄʀᴇᴇɴꜱʜᴏᴛ", callback_data="screenshot")],
        [InlineKeyboardButton("Tʀɪᴍ", callback_data="trim")],
        [InlineKeyboardButton("Exᴛʀᴀᴄᴛ Aᴜᴅɪᴏ", callback_data="extract_audio")],
        [InlineKeyboardButton("🆘 Support", url="https://t.me/YourSupportGroup")]
    ]

    await message.reply_text(
        "<b>Here is your permanent stream & download link:</b>\n\n",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML,
        quote=True
    )

    # 7. Log It
    await log_msg.reply_text(
        "#LinkGenerated\n\n👤 User: {username}\n🆔 ID: <code>{user_id}</code>\n📄 File: {file_name}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("▶️ Watch", url=stream_url)]])
    )
@Client.on_message(filters.command("start") & filters.chat(-1002687879857))
async def sydstart(client, message):
    await message.reply_text(".")
