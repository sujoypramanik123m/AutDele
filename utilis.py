import logging
import asyncio
import pytz
import random 
import re
import os
from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid

AUTH_CHANNEL = Config.AUTH_CHANNEL

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
