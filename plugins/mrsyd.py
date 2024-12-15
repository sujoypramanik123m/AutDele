from pyrogram import Client
import asyncio



@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    if message.chat.id != -1001605140211:
        return
    await asyncio.sleep(40)
    await message.delete()
