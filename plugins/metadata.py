from pyrogram import Client, filters
from pyrogram.types import Message
from helper.database import db
from pyromod.exceptions import ListenerTimeout
from config import Txt
from plugins.features import features_button


@Client.on_message(filters.private & filters.command('metadata'))
async def handle_metadata(bot: Client, message: Message):

    ms = await message.reply_text("**Please Wait...**")
    user_metadata = await db.get_metadata_code(message.from_user.id)
    markup = await features_button(message.from_user.id)

    await ms.edit(f'**Hᴇʀᴇ ɪꜱ ᴛʜᴇ ᴀᴠᴀɪʟᴀʙʟᴇ ғᴇᴀᴛᴜʀᴇ** 🍀**\n\nYᴏᴜʀ Cᴜʀʀᴇɴᴛ Mᴇᴛᴀᴅᴀᴛᴀ:-\n\n➜ `{user_metadata}` \nUꜱᴇ /set_metadata ᴛᴏ ᴄʜᴀɴɢᴇ ᴍᴇᴛᴀᴅᴀᴛᴀ 😔', reply_markup=markup)


@Client.on_message(filters.private & filters.command('set_metadata'))
async def handle_set_metadata(bot: Client, message: Message):
    try:
        metadata = await bot.ask(text=Txt.SEND_METADATA, chat_id=message.from_user.id, filters=filters.text, timeout=30, disable_web_page_preview=True)
    except ListenerTimeout:
        await message.reply_text("⚠️ Error!!\n\n**Request timed out.**\nRestart by using /set_metadata", reply_to_message_id=message.id)
        return
    print(metadata.text)
    ms = await message.reply_text("**Please Wait...**", reply_to_message_id=metadata.id)
    await db.set_metadata_code(message.from_user.id, metadata_code=metadata.text)
    await ms.edit("**Yᴏᴜʀ Mᴇᴛᴀᴅᴀᴛᴀ Cᴏᴅᴇ Sᴇᴛ Sᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ✅**")
