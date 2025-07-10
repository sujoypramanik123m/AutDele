import random, re
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
from syd import send_log
logger = logging.getLogger(__name__)
CHID = -1002794399929
@Client.on_message(filters.private & filters.command("start"))
async def start(client, message):

    if message.from_user.id in Config.BANNED_USERS:
        await message.reply_text("Sorry, You are banned.")
        return

    user = message.from_user
    
    if not await db.users.find_one({"_id": user.id}):
        await db.add_user(user.id)
        await send_log(client, message)
    try:
        await client.get_chat_member(CHID, message.from_user.id)
    except UserNotParticipant:
        
        key = InlineKeyboardMarkup(
            [[
                InlineKeyboardButton("↱ Jᴏɪɴ Cʜᴀɴɴᴇʟ ↲", url="https://t.me/ProToppers"),
                InlineKeyboardButton("Cᴏɴᴛɪɴᴜᴇ ↯", callback_data="chk")
            ]]
        )
        await message.reply_text("**Pʟᴇᴀꜱᴇ Jᴏɪɴ Iɴ Oᴜʀ Cʜᴀɴɴᴇʟ Tᴏ Uꜱᴇ Mᴇ 🥶.\nIꜰ Yᴏᴜ Jᴏɪɴᴇᴅ Tʜᴇ Cʜᴀɴɴᴇʟ Tʜᴇɴ Cʟɪᴄᴋ Oɴ Cᴏɴᴛɪɴᴜᴇ Bᴜᴛᴛᴏɴ Tᴏ Pʀᴏᴄᴇꜱꜱ ✨.\n\n__Jᴏɪɴ: @ProToppers 🌡️__**", reply_markup=key)
        return 
    except Exception as e:
        try:
            await client.send_message(8181241262, f"Fsub: {e}")
        except:
            pass
    button = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            'Uᴘᴅᴀᴛᴇꜱ ¹', url='https://t.me/ProToppers'),
        InlineKeyboardButton(
            'Sᴜᴘᴘᴏʀᴛ', url='https://t.me/SuperToppers0')],
        [InlineKeyboardButton('Oᴡɴᴇʀ', user_id=8181241262)
    ], [
        InlineKeyboardButton('Bᴏᴛꜱ', url='https://t.me/ProToppers'),
        InlineKeyboardButton('Uᴩᴅᴀᴛᴇꜱ ²', url='https://t.me/SuperToppers0')]])
    if Config.PICS:
        await message.reply_photo(random.choice(Config.PICS), caption=Txt.STRT_TXT.format(user.mention), reply_markup=button)
    else:
        await message.reply_text(text=Txt.STRT_TXT.format(user.mention), reply_markup=button, disable_web_page_preview=True)


@Client.on_callback_query(filters.regex("chk"))
async def chk(_, cb : CallbackQuery):
    try:
        await _.get_chat_member(CHID, cb.from_user.id)
    except:
        await cb.answer("You ᴀʀᴇ ɴᴏᴛ ᴊᴏɪɴᴇᴅ ɪɴ ᴍʏ ᴄʜᴀɴɴᴇʟ, ᴊᴏɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ᴛʜᴇɴ ᴄʜᴇᴄᴋ ᴀɢᴀɪɴ. 🎐", show_alert=True)
        return 

    user = cb.from_user
    button = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            'Uᴘᴅᴀᴛᴇꜱ ¹', url='https://t.me/SuperToppers'),
        InlineKeyboardButton(
            'Sᴜᴘᴘᴏʀᴛ', url='https://t.me/SuperToppers0')],
        [InlineKeyboardButton('Oᴡɴᴇʀ', user_id=8181241262)
    ], [
        InlineKeyboardButton('Bᴏᴛꜱ', url='https://t.me/ProToppers'),
        InlineKeyboardButton('Uᴩᴅᴀᴛᴇꜱ ²', url='https://t.me/SuperToppers0')]])
    if Config.PICS:
        await cb.message.reply_photo(random.choice(Config.PICS), caption=Txt.STRT_TXT.format(user.mention), reply_markup=button)
    else:
        await cb.message.reply_text(text=Txt.STRT_TXT.format(user.mention), reply_markup=button, disable_web_page_preview=True)

LINK_REGEX = re.compile(r"(https?://|www\.|t\.me/|telegram\.me/|bit\.ly|goo\.gl|@)")

@Client.on_message(filters.group & ~filters.service)
async def delete_message(bot: Client, message: Message):
    await db.add_grp(message.chat.id)

    # skip non-text messages
    if not message.text:
        return

    user_id = message.from_user.id
    try:
        user = await bot.get_chat_member(message.chat.id, user_id)
        user_status = user.status
    except:
        user_status = None

    if (
        user_status == enums.ChatMemberStatus.ADMINISTRATOR
        or user_status == enums.ChatMemberStatus.OWNER
        or user_id in Config.ADMIN
    ):
        return

    text = message.text.lower()
    words = text.split()

    text = message.text.lower()

    text = text.replace("@admin", "")

    # check plain text links
    if LINK_REGEX.search(text):
        try:
            await message.delete()
        except Exception:
            pass
        return

    # check hyperlinks in entities
    if message.entities:
        for entity in message.entities:
            if entity.type == enums.MessageEntityType.TEXT_LINK:
                try:
                    await message.delete()
                except Exception:
                    pass
                return


from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid
import os
import sys
import time
import asyncio
import logging
import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@Client.on_message(filters.command(["stats", "status"]) & filters.user(Config.ADMIN))
async def get_stats(bot, message):
    total_users = await db.total_users_count()
    total_grp = await db.total_grps_count()
    uptime = time.strftime("%Hh%Mm%Ss", time.gmtime(
        time.time() - Config.BOT_UPTIME))
    start_t = time.time()
    st = await message.reply('**Aᴄᴄᴇꜱꜱɪɴɢ Tʜᴇ Dᴇᴛᴀɪʟꜱ.....**')
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    await st.edit(text=f"**--Bᴏᴛ Sᴛᴀᴛᴜꜱ--** \n\n**⌚️ Bᴏᴛ Uᴩᴛɪᴍᴇ:** {uptime} \n**🐌 Cᴜʀʀᴇɴᴛ Pɪɴɢ:** `{time_taken_s:.3f} ᴍꜱ` \n**👭 Tᴏᴛᴀʟ Uꜱᴇʀꜱ:** `{total_users}`\n 🍹Tᴏᴛᴀʟ Gʀᴏᴜᴩꜱ: `{total_grp}`")


# Restart to cancell all process
@Client.on_message(filters.private & filters.command("restart") & filters.user(Config.ADMIN))
async def restart_bot(b, m):
    await m.reply_text("🔄__Rᴇꜱᴛᴀʀᴛɪɴɢ.....__")
    os.execl(sys.executable, sys.executable, *sys.argv)


@Client.on_message(filters.command("broadcast") & filters.user(Config.ADMIN) & filters.reply)
async def broadcast_handler(bot: Client, m: Message):
    await bot.send_message(Config.LOG_CHANNEL, f"{m.from_user.mention} or {m.from_user.id} Iꜱ ꜱᴛᴀʀᴛᴇᴅ ᴛʜᴇ Bʀᴏᴀᴅᴄᴀꜱᴛ......")
    all_users = await db.get_all_users()
    broadcast_msg = m.reply_to_message
    sts_msg = await m.reply_text("Bʀᴏᴀᴅᴄᴀꜱᴛ Sᴛᴀʀᴛᴇᴅ..!")
    done = 0
    failed = 0
    success = 0
    start_time = time.time()
    total_users = await db.total_users_count()
    async for user in all_users:
        sts = await send_msg(user['_id'], broadcast_msg)
        if sts == 200:
            success += 1
        else:
            failed += 1
        if sts == 400:
            await db.delete_user(user['_id'])
        done += 1
        if not done % 20:
            await sts_msg.edit(f"Bʀᴏᴀᴅᴄᴀꜱᴛ Iɴ Pʀᴏɢʀᴇꜱꜱ: \nTᴏᴛᴀʟ Uꜱᴇʀꜱ {total_users} \nCᴏᴍᴩʟᴇᴛᴇᴅ: {done} / {total_users}\nSᴜᴄᴄᴇꜱꜱ: {success}\nFᴀɪʟᴇᴅ: {failed}")
    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts_msg.edit(f"Bʀᴏᴀᴅᴄᴀꜱᴛ Cᴏᴍᴩʟᴇᴛᴇᴅ: \nCᴏᴍᴩʟᴇᴛᴇᴅ Iɴ `{completed_in}`.\n\nTᴏᴛᴀʟ Uꜱᴇʀꜱ {total_users}\nCᴏᴍᴩʟᴇᴛᴇᴅ: {done} / {total_users}\nSᴜᴄᴄᴇꜱꜱ: {success}\nFᴀɪʟᴇᴅ: {failed}")


@Client.on_message(filters.command("group_broadcast") & filters.user(Config.ADMIN) & filters.reply)
async def broadcst_handler(bot: Client, m: Message):
    await bot.send_message(Config.LOG_CHANNEL, f"{m.from_user.mention} or {m.from_user.id} Iꜱ ꜱᴛᴀʀᴛᴇᴅ ᴛʜᴇ Gʀᴩ Bʀᴏᴀᴅᴄᴀꜱᴛ......")
    all_grps = await db.get_all_grps()
    broadcast_msg = m.reply_to_message
    sts_msg = await m.reply_text("Bʀᴏᴀᴅᴄᴀꜱᴛ Sᴛᴀʀᴛᴇᴅ..!")
    done = 0
    failed = 0
    success = 0
    start_time = time.time()
    total_grps = await db.total_grps_count()
    async for user in all_grps:
        sts = await send_msg(user['_id'], broadcast_msg)
        if sts == 200:
            success += 1
        else:
            failed += 1
        if sts == 400:
            await m.reply(f"Cant Send To {user['_id']}")
        done += 1
        if not done % 20:
            await sts_msg.edit(f"Bʀᴏᴀᴅᴄᴀꜱᴛ Iɴ Pʀᴏɢʀᴇꜱꜱ: \nTᴏᴛᴀʟ Uꜱᴇʀꜱ {total_users} \nCᴏᴍᴩʟᴇᴛᴇᴅ: {done} / {total_users}\nSᴜᴄᴄᴇꜱꜱ: {success}\nFᴀɪʟᴇᴅ: {failed}")
    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts_msg.edit(f"Bʀᴏᴀᴅᴄᴀꜱᴛ Cᴏᴍᴩʟᴇᴛᴇᴅ: \nCᴏᴍᴩʟᴇᴛᴇᴅ Iɴ `{completed_in}`.\n\nTᴏᴛᴀʟ Uꜱᴇʀꜱ {total_users}\nCᴏᴍᴩʟᴇᴛᴇᴅ: {done} / {total_users}\nSᴜᴄᴄᴇꜱꜱ: {success}\nFᴀɪʟᴇᴅ: {failed}")


async def send_msg(user_id, message):
    try:
        await message.forward(chat_id=int(user_id))
        return 200
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return send_msg(user_id, message)
    except InputUserDeactivated:
        logger.info(f"{user_id} : Dᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ")
        return 400
    except UserIsBlocked:
        logger.info(f"{user_id} : Bʟᴏᴄᴋᴇᴅ Tʜᴇ Bᴏᴛ")
        return 400
    except PeerIdInvalid:
        logger.info(f"{user_id} : Uꜱᴇʀ Iᴅ Iɴᴠᴀʟɪᴅ")
        return 400
    except Exception as e:
        logger.error(f"{user_id} : {e}")
        return 500

