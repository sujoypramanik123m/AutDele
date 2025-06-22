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


@Client.on_message(filters.private & filters.command("disclaimer"))
async def disclaimer(client, message):
    await message.reply_text(
        text="""ᴅɪꜱᴄʟᴀɪᴍᴇʀ:
                ɴᴇᴠᴇʀ ꜱᴇɴᴅ ᴩᴇʀꜱᴏɴᴀʟ ꜰɪʟᴇꜱ, ꜱɪɴᴄᴇ ᴛʜᴇʏ ᴀʀᴇ ꜱᴛᴏʀᴇᴅ ᴛᴏ ꜰɪɴᴅ ᴀɴʏ ꜱᴜꜱᴩɪᴄɪᴏᴜꜱ ᴀᴄᴛɪᴠɪᴛʏ ᴅᴏɴᴇ ʙʏ ᴛʜᴇ ᴜꜱᴇʀꜱ
                ᴀʟᴡᴀʏ ᴜꜱᴇ ᴛʜᴇ ʙᴏᴛ ᴩʀᴏᴩᴇʀʟʏ ᴀɴᴅ ᴛᴀᴋᴇ ʀᴇꜱᴩᴏɴꜱɪʙɪʟᴛʏ ᴏꜰ ᴛʜᴇ ꜰɪʟᴇ, ᴛʜᴇʏ ᴀʀᴇ ʏᴏᴜʀ ᴩʀᴏᴩᴇʀᴛɪᴇꜱ ꜱᴏ ᴛʜᴇ ꜰɪʟᴇꜱ ᴀᴛ ʏᴏᴜʀ ᴏᴡɴ ʀɪꜱᴋ.
                ꜱʜᴀʀɪɴɢ ᴀᴅᴜʟᴛ ꜰɪʟᴇꜱ ᴡɪʟʟ ʟᴇᴀᴅ ᴛᴏ ʏᴏᴜʀ ʙᴀɴ, ᴀɴᴅ ꜰᴜʀᴛʜᴇʀ ʏᴏᴜ ᴍᴀʏ ɴᴏᴛ ʙᴇ ᴀʙʟᴇ ᴛᴏ ᴜꜱᴇ ᴛʜᴇ ʙᴏᴛ.""", 
        disable_web_page_preview=True
    )
    
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
import asyncio, re

# --- Constants ---
SYD_CHANNELS = ["@MainChannel", "@AnotherChannel"]
SYD_BACKUP_LINK = "https://t.me/backup_channel"


# --- Time Parser ---
def parse_time(time_str):
    match = re.match(r'^(\d+)([smh])$', time_str.lower())
    if not match:
        return None
    value, unit = match.groups()
    value = int(value)
    return value * {"s": 1, "m": 60, "h": 3600}[unit]


# --- Bot Admin Check ---
async def is_bot_admin(bot: Client, chat_id: int):
    try:
        member = await bot.get_chat_member(chat_id, 'me')
        return member.status in ['administrator', 'creator']
    except Exception:
        return False


async def ensure_member(client, msg):
    """
    Ensures the user is in all required SYD_CHANNELS and private chats (REQUIRED_CHAT_IDS).
    Sends join/invite buttons if not.
    """
    user_id = msg.from_user.id
    replyable = msg.message if hasattr(msg, "message") else msg

    not_joined = []

    # Check public channels (username-based)
    for ch in SYD_CHANNELS:
        try:
            member = await client.get_chat_member(ch, user_id)
            if member.status in {"left", "kicked"}:
                not_joined.append(("channel", ch))
        except UserNotParticipant:
            not_joined.append(("channel", ch))
        except Exception:
            pass

    # Check private groups/chats by ID
    for chat_id in REQUIRED_CHAT_IDS:
        try:
            member = await client.get_chat_member(chat_id, user_id)
            if member.status in {"left", "kicked"}:
                not_joined.append(("private", chat_id))
        except (UserNotParticipant, PeerIdInvalid, ChatAdminRequired):
            not_joined.append(("private", chat_id))
        except Exception:
            pass

    if not not_joined:
        return True

    # Build button rows
    join_buttons = []

    for kind, chat in not_joined:
        if kind == "channel":
            join_buttons.append([
                InlineKeyboardButton(
                    text=f"✧ Join {str(chat).replace('_', ' ').title()} ✧",
                    url=f"https://t.me/{str(chat).lstrip('@')}"
                )
            ])
        elif kind == "private":
            invite_link = CHAT_INVITE_LINKS.get(chat)
            if invite_link:
                join_buttons.append([
                    InlineKeyboardButton(
                        text="✧ Join Private Chat ✧",
                        url=invite_link
                    )
                ])

    join_buttons.append([
        InlineKeyboardButton("☑ Joined ☑", callback_data="check_subscription")
    ])

    await replyable.reply_text(
        text="**Please join all required channels and chats to continue.**",
        reply_markup=InlineKeyboardMarkup(join_buttons),
        quote=True,
        disable_web_page_preview=True
    )
    return False



# --- /setdelete ---
@Client.on_message(filters.command("setdelete"))
async def set_delete_handler(bot, message: Message):
    if not await ensure_member(bot, message):
        return

    args = message.text.split()

    if message.chat.type in ["group", "supergroup"]:
        if len(args) != 2:
            return await message.reply("⚠️ Usage: `/setdelete 30s`, `2m`, or `1h`", quote=True)

        time_sec = parse_time(args[1])
        if not time_sec:
            return await message.reply("❌ Invalid format. Use `s`, `m`, or `h`.")

        if not await is_bot_admin(bot, message.chat.id):
            return await message.reply("❌ I need to be admin to delete messages.")

        await db.col.update_one(
            {"chat_id": message.chat.id},
            {"$set": {"delete_after": time_sec}},
            upsert=True
        )
        await message.reply(f"✅ Messages will auto-delete after {time_sec} seconds.")

    elif message.chat.type == "private":
        if len(args) != 3:
            return await message.reply("⚠️ Usage: `/setdelete <chat_id> <time>`", quote=True)

        try:
            chat_id = int(args[1])
        except ValueError:
            return await message.reply("❌ Invalid chat ID.")

        time_sec = parse_time(args[2])
        if not time_sec:
            return await message.reply("❌ Invalid time format.")

        if not await is_bot_admin(bot, chat_id):
            return await message.reply("❌ I must be admin in that group.")

        await db.col.update_one(
            {"chat_id": chat_id},
            {"$set": {"delete_after": time_sec}},
            upsert=True
        )
        await message.reply(f"✅ Messages will auto-delete in `{chat_id}` after {time_sec} seconds.")


# --- /getdelete ---
@Client.on_message(filters.command("getdelete") & filters.group)
async def get_delete_handler(bot, message: Message):
    config = await db.col.find_one({"chat_id": message.chat.id})
    if config and config.get("delete_after"):
        seconds = config["delete_after"]
        await message.reply(f"🕒 Current auto-delete time: **{seconds} seconds**.")
    else:
        await message.reply("❌ Auto-delete is not set in this group.")


# --- /deldelete ---
@Client.on_message(filters.command("deldelete") & filters.group)
async def del_delete_handler(bot, message: Message):
    await db.col.delete_one({"chat_id": message.chat.id})
    await message.reply("✅ Auto-delete has been removed for this group.")


# --- Auto Delete Group Messages ---
@Client.on_message(filters.group & ~filters.service)
async def auto_delete_message(bot: Client, message: Message):
    config = await db.col.find_one({"chat_id": message.chat.id})
    if config and config.get("delete_after"):
        delay = config["delete_after"]
        await asyncio.sleep(delay)
        try:
            await message.delete()
        except:
            pass
