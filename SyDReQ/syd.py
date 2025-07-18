from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, ChatJoinRequest
from pyrogram import filters, Client, errors, enums
from pyrogram.errors import UserNotParticipant
from pyrogram.errors.exceptions.flood_420 import FloodWait
from .database import add_user, add_group, all_users, all_groups, users, remove_user, already_db
from config import Config
import random, asyncio
from syd import send_log
CHID = -1001541018556
@Client.on_chat_join_request()
async def handle_join_request(client: Client, join_request: ChatJoinRequest):
    user_id = join_request.from_user.id
    chat_id = join_request.chat.id

    # Approve the join request
    await client.approve_chat_join_request(chat_id, user_id)

    # Prepare an inline keyboard
    syd = InlineKeyboardMarkup(
        [[
         InlineKeyboardButton("✦ Uᴩᴅᴀᴛᴇꜱ", url=f"https://t.me/bot_Cracker"),
         InlineKeyboardButton("Cʜᴀɴɴᴇʟ ✦", url=f"https://t.me/Mod_Moviez_X")
        ],[
         InlineKeyboardButton("◈ Mᴏʀᴇ ◈", url=f"https://t.me/Instant_Approval_Bot?start=")
        ]]
    )
    try:
        await client.send_message(
            chat_id=user_id,
            text="Yᴏᴜʀ RᴇQᴜᴇꜱᴛ Tᴏ Jᴏɪɴ Tʜᴇ Cʜᴀᴛ Hᴀꜱ Bᴇᴇɴ Aᴄᴄᴇᴩᴛᴇᴅ Iɴꜱᴛᴀɴᴛʟʏ! 🎍 \nTᴀᴩ Bᴇʟᴏᴡ Bᴜᴛᴛᴏɴ Tᴏ Kɴᴏᴡ Mᴏʀᴇ..! 🕯️",
            reply_markup=syd
        )
    except Exception as e:
        print(f"Failed to send message to user: {e}")

    if not already_db(user_id):
        add_user(user_id)
        await send_log(client, join_request)

 
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Start ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_message(filters.private & filters.command("start"))
async def op(_, m :Message):
    try:
        await _.get_chat_member(CHID, m.from_user.id)
    except Exception as e:
        print(f"User not in channel: {e}")
        key = InlineKeyboardMarkup(
            [[
                InlineKeyboardButton("↱ Jᴏɪɴ Cʜᴀɴɴᴇʟ ↲", url="https://t.me/bot_Cracker"),
                InlineKeyboardButton("Cᴏɴᴛɪɴᴜᴇ ↯", callback_data="chk")
            ]]
        )
        await m.reply_text("**Pʟᴇᴀꜱᴇ Jᴏɪɴ Iɴ Oᴜʀ Cʜᴀɴɴᴇʟ Tᴏ Uꜱᴇ Mᴇ 🥶.\nIꜰ Yᴏᴜ Jᴏɪɴᴇᴅ Tʜᴇ Cʜᴀɴɴᴇʟ Tʜᴇɴ Cʟɪᴄᴋ Oɴ Cᴏɴᴛɪɴᴜᴇ Bᴜᴛᴛᴏɴ Tᴏ Pʀᴏᴄᴇꜱꜱ ✨.\n\n__Jᴏɪɴ: @Bot_Cracker 🌡️__**", reply_markup=key)
        return 
    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("⨭ Aᴅᴅ ᴛᴏ ɢʀᴏᴜᴩ ⨮", url="https://t.me/Instant_Approval_Bot?startgroup=syd_grp")
        ],[
            InlineKeyboardButton("✦ Uᴩᴅᴀᴛᴇꜱ", url="https://t.me/bot_Cracker"),
            InlineKeyboardButton("Cʜᴀɴɴᴇʟ ✦", url="https://t.me/Mod_Moviez_X")
        ],[
            InlineKeyboardButton("⨭ Aᴅᴅ ᴛᴏ ᴄʜᴀɴɴᴇʟ ⨮", url="https://t.me/Instant_Approval_Bot?startchannel=syd_chnl")
        ]]

    )
    
    if not already_db(m.from_user.id):
        try:
            await send_log(_, m)
        except Exception as e:
            print(f"{e}")
        add_user(m.from_user.id)
    await m.reply_photo("https://i.ibb.co/5xx6Xd3w/file-1426.jpg", caption="**ʜᴇʏ {}!\n\nɪ'ᴍ ᴀɴ ɪɴꜱᴛᴀɴᴛ ᴀᴩᴩʀᴏᴠᴀʟ ʙᴏᴛ [ᴀᴄᴄᴇᴩᴛ ᴊᴏɪɴ ʀᴇqᴜᴇꜱᴛꜱ] ʙᴏᴛ.\nɪ ᴄᴀɴ ᴀᴩᴩʀᴏᴠᴇ ᴜꜱᴇʀꜱ ɪɴ ɢʀᴏᴜᴩ/ᴄʜᴀɴɴᴇʟꜱ. ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ᴄʜᴀᴛ ᴀɴᴅ ᴩʀᴏᴍᴏᴛᴇ ᴍᴇ ᴛᴏ ᴀᴅᴍɪɴ ᴡɪᴛʜ ɪɴᴠɪᴛᴇ ᴩᴇʀᴍɪꜱꜱɪᴏɴ.\n\n__Pᴏᴡᴇʀᴇᴅ Bʏ : @Mod_Moviez_X __**".format(m.from_user.mention), reply_markup=keyboard)
    

#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ callback ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_callback_query(filters.regex("chk"))
async def chk(_, cb : CallbackQuery):
    try:
        await _.get_chat_member(CHID, cb.from_user.id)
    except:
        await cb.answer("You ᴀʀᴇ ɴᴏᴛ ᴊᴏɪɴᴇᴅ ɪɴ ᴍʏ ᴄʜᴀɴɴᴇʟ, ᴊᴏɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ᴛʜᴇɴ ᴄʜᴇᴄᴋ ᴀɢᴀɪɴ. 🎐", show_alert=True)
        return 
    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("⨭ Aᴅᴅ ᴛᴏ ɢʀᴏᴜᴩ ⨮", url="https://t.me/Instant_Approval_Bot?startgroup=syd_grp")
        ],[
            InlineKeyboardButton("✦ Uᴩᴅᴀᴛᴇꜱ", url="https://t.me/bot_Cracker"),
            InlineKeyboardButton("Cʜᴀɴɴᴇʟ ✦", url="https://t.me/Mod_Moviez_X")
        ],[
            InlineKeyboardButton("⨭ Aᴅᴅ ᴛᴏ ᴄʜᴀɴɴᴇʟ ⨮", url="https://t.me/Instant_Approval_Bot?startchannel=syd_chnl")
        ]]

    )
    add_user(cb.from_user.id)
    await cb.edit_text(text="**ʜᴇʏ {}!\n\nɪ'ᴍ ᴀɴ ɪɴꜱᴛᴀɴᴛ ᴀᴩᴩʀᴏᴠᴀʟ ʙᴏᴛ [ᴀᴄᴄᴇᴩᴛ ᴊᴏɪɴ ʀᴇqᴜᴇꜱᴛꜱ] ʙᴏᴛ.\nɪ ᴄᴀɴ ᴀᴩᴩʀᴏᴠᴇ ᴜꜱᴇʀꜱ ɪɴ ɢʀᴏᴜᴩ/ᴄʜᴀɴɴᴇʟꜱ. ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ᴄʜᴀᴛ ᴀɴᴅ ᴩʀᴏᴍᴏᴛᴇ ᴍᴇ ᴛᴏ ᴀᴅᴍɪɴ ᴡɪᴛʜ ɪɴᴠɪᴛᴇ ᴩᴇʀᴍɪꜱꜱɪᴏɴ.\n\n__Pᴏᴡᴇʀᴇᴅ Bʏ : @Bot_Cracker __**".format(cb.from_user.mention), reply_markup=keyboard)
    
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ info ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_message(filters.command("users") & filters.user(Config.ADMIN))
async def dbtool(_, m : Message):
    xx = all_users()
    x = all_groups()
    tot = int(xx + x)
    await m.reply_text(text=f"""
🍀 Chats Stats 🍀
🙋‍♂️ Users : `{xx}`
👥 Groups : `{x}`
🚧 Total users & groups : `{tot}` """)

#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Broadcast ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_message(filters.command("bcast") & filters.user(Config.ADMIN))
async def bcast(_, m : Message):
    allusers = users
    lel = await m.reply_text("`⚡️ Processing...`")
    success = 0
    failed = 0
    deactivated = 0
    blocked = 0
    for usrs in allusers.find():
        try:
            userid = usrs["user_id"]
            #print(int(userid))
            if m.command[0] == "bcast":
                await m.reply_to_message.copy(int(userid))
            success +=1
        except FloodWait as ex:
            await asyncio.sleep(ex.value)
            if m.command[0] == "bcast":
                await m.reply_to_message.copy(int(userid))
        except errors.InputUserDeactivated:
            deactivated +=1
            remove_user(userid)
        except errors.UserIsBlocked:
            blocked +=1
        except Exception as e:
            print(e)
            failed +=1

    await lel.edit(f"✅Successfull to `{success}` users.\n❌ Faild to `{failed}` users.\n👾 Found `{blocked}` Blocked users \n👻 Found `{deactivated}` Deactivated users.")

#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Broadcast Forward ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_message(filters.command("fcast") & filters.user(Config.ADMIN))
async def fcast(_, m : Message):
    allusers = users
    lel = await m.reply_text("`⚡️ Processing...`")
    success = 0
    failed = 0
    deactivated = 0
    blocked = 0
    for usrs in allusers.find():
        try:
            userid = usrs["user_id"]
            #print(int(userid))
            if m.command[0] == "fcast":
                await m.reply_to_message.forward(int(userid))
            success +=1
        except FloodWait as ex:
            await asyncio.sleep(ex.value)
            if m.command[0] == "fcast":
                await m.reply_to_message.forward(int(userid))
        except errors.InputUserDeactivated:
            deactivated +=1
            remove_user(userid)
        except errors.UserIsBlocked:
            blocked +=1
        except Exception as e:
            print(e)
            failed +=1

    await lel.edit(f"✅Successfull to `{success}` users.\n❌ Faild to `{failed}` users.\n👾 Found `{blocked}` Blocked users \n👻 Found `{deactivated}` Deactivated users.")
