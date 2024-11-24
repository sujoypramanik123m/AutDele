from time import sleep
from pyrogram import Client, filters
from threading import Thread

from pyrogram import Client, filters
import logging
import asyncio

# Logging setup
logging.basicConfig(level=logging.INFO)

# Shared queue and processing flag
file_queue = []
processing = False
current_channel_index = 0
sydtg = -1002305372915
Syd_T_G = -1002160523059
# Channel IDs and constants
CHANNELS = ["-1002464733363", "-1002429058090", "-1002433450358"]
MSYD = -1002377676305  # Source chat ID


async def process_queue(client):
    """Processes files in the queue and forwards them to specified channels."""
    global processing, current_channel_index

    while file_queue:
        sydfile = file_queue.pop(0)  # Get the first file in the queue
        file_name = sydfile['file_name']
        media = sydfile['media']
        message = sydfile['message']

        channel = CHANNELS[current_channel_index]
        current_channel_index = (current_channel_index + 1) % len(CHANNELS)

        try:
            await client.send_document(channel, media.file_id, caption=f"Forwarded: {file_name}")
            logging.info(f"File {file_name} forwarded to {channel}.")
        except Exception as e:
            logging.error(f"Error forwarding {file_name} to {channel}: {e}")

        await asyncio.sleep(80)

    processing = False

@Client.on_message(filters.document | filters.audio | filters.video)
async def syd_file(client, message):
    global processing
    if message.chat.id == MSYD:  # Ensure the file is from the specified chat
        try:
            file = getattr(message, message.media.value)  # Get the media object
            if not file:
                return

            if file.file_size > 2000 * 1024 * 1024:  # > 2 GB
                from_syd = message.chat.id
                syd_id = message.id
                await client.copy_message(sydtg, from_syd, syd_id)
                await message.delete()
                return
            if file.file_size < 1024 * 1024:  # < 1 MB
                from_syd = message.chat.id
                syd_id = message.id
                await client.copy_message(Syd_T_G, from_syd, syd_id)
                await message.delete()
                return
                
            # Prepare file metadata for forwarding
            sydfile = {
                'file_name': file.file_name,
                'file_size': file.file_size,
                'message_id': message.id,
                'media': file,
                'message': message
            }
            file_queue.append(sydfile)  # Add to the queue
            logging.info(f"File {file.file_name} added to the queue.")
            if not processing:
                processing = True
                await process_queue(client)

        except Exception as e:
            logging.error(f"Error handling file: {e}")
