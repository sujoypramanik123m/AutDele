from time import sleep
from pyrogram import Client, filters
from threading import Thread
import json
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
CHANNELS = ["-1002464733363", "-1002429058090", "-1002433450358", "-1002280144341"]
MSYD = -1002377676305  # Source chat ID
SYD = [2, 5, 8, 1, 10]

try:
    with open("processed_files.json", "r") as f:
        processed_files = set(json.load(f))
except FileNotFoundError:
    processed_files = set()

def save_processed_files():
    """Saves the processed file IDs to a JSON file."""
    with open("processed_files.json", "w") as f:
        json.dump(list(processed_files), f)

async def process_queue(client):
    global processing, current_channel_index

    while file_queue:
        sydfile = file_queue.pop(0)  # Get the first file in the queue
        file_name = sydfile['file_name']
        media = sydfile['media']
        message = sydfile['message']

        channel = CHANNELS[current_channel_index]
        current_channel_index = (current_channel_index + 1) % len(CHANNELS)

        try:
            if message.video:  
                await client.send_video(
                    channel, 
                    media.file_id, 
                    caption=f"ᴍʀ ꜱʏᴅ: {file_name}"
                )
                logging.info(f"Video {file_name} forwarded to {channel}.")
            else:
                await client.send_document(
                    channel, 
                    media.file_id, 
                    caption=f"ᴍʀ ꜱʏᴅ: {file_name}"
                )
                #logging.info(f"File {file_name} forwarded to {channel}.")
            await message.delete()
        except Exception as e:
            logging.error(f"Error forwarding {file_name} to {channel}: {e}")
            await message.react("👀")
        await asyncio.sleep(100)
    processing = False

@Client.on_message(filters.document | filters.audio | filters.video)
async def syd_file(client, message):
    global processing
    if message.chat.id == MSYD:  # Ensure the file is from the specified chat
        try:
            file = getattr(message, message.media.value)  # Get the media object
            if not file:
                return

            file_metadata = (file.file_name, file.file_size)
            if file_metadata in processed_files:
                logging.info(f"Duplicate file {file.file_name} (Size: {file.file_size}) ignored.")
                await message.react("⚡")
                return

            if file.file_size > 2000 * 1024 * 1024:  # > 2 GB
                from_syd = message.chat.id
                syd_id = message.id
                await asyncio.sleep(random.choice(SYD))
                await client.copy_message(sydtg, from_syd, syd_id)
                await message.delete()
                return
            if file.file_size < 1024 * 1024:  # < 1 MB
                from_syd = message.chat.id
                syd_id = message.id
                await asyncio.sleep(random.choice(SYD))
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
            processed_files.add(file_metadata)  # Mark file as processed
            save_processed_files()  # Persist updates
            logging.info(f"File {file.file_name} added to the queue.")
            
            if not processing:
                processing = True
                await process_queue(client)

        except Exception as e:
            logging.error(f"Error handling file: {e}")
