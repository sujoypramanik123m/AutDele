import logging
import asyncio
import pytz
import random 
import re
from pytz import timezone
import os
from helper.database import db
from config import Config
from info import AUTH_CHANNEL
from pyrogram.types import Message
from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
import time
import logging
from datetime import datetime
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

async def send_log(b, message):
    if Config.LOG_CHANNEL is not None:
        curr = datetime.now(timezone("Asia/Kolkata"))
        date = curr.strftime("%d %B, %Y")
        time_str = curr.strftime("%I:%M:%S %p")
        me = await b.get_me()
        u = message.from_user
        try:
            await b.send_message(
                Config.LOG_CHANNEL,
                f"**--Nᴇᴡ Uꜱᴇʀ Sᴛᴀʀᴛᴇᴅ Tʜᴇ Bᴏᴛ--**\n\n"
                f"Uꜱᴇʀ: {u.mention}\nIᴅ: `{u.id}`\nUɴ: @{u.username}\n\n"
                f"Dᴀᴛᴇ: {date}\nTɪᴍᴇ: {time_str}\n\n"
                f"By: @{me.username}"
            )
        except Exception as e:
            for mrsyd in Config.ADMIN:
                await b.send_message(
                    mrsyd, 
                    f"**--Nᴇᴡ Uꜱᴇʀ Sᴛᴀʀᴛᴇᴅ Tʜᴇ Bᴏᴛ--**\n\n"
                f"Uꜱᴇʀ: {u.mention}\nIᴅ: `{u.id}`\nUɴ: @{u.username}\n\n"
                f"Dᴀᴛᴇ: {date}\nTɪᴍᴇ: {time_str}\n\n"
                f"By: @{me.username}, {e}"
                )

async def is_req_subscribed(bot, query):
    if await db.find_join_req(query.from_user.id):
        return True
    try:
        user = await bot.get_chat_member(AUTH_CHANNEL, query.from_user.id)
    except UserNotParticipant:
        pass
    except Exception as e:
        logger.exception(e)
    else:
        if user.status != enums.ChatMemberStatus.BANNED:
            return True

    return False
