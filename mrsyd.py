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

# Channel IDs and constants
CHANNELS = ["-1002464733363", "-1002429058090", "-1002433450358"]
MSYD = -1002377676305  # Source chat ID


async def process_queue(client):
    """Processes files in the queue and forwards them to specified channels."""
    global processing

    while file_queue:
        sydfile = file_queue.pop(0)  # Get the first file in the queue
        file_name = sydfile['file_name']
        media = sydfile['media']
        message = sydfile['message']

        # Round-robin
        for channel in CHANNELS:
            try:
                await client.send_document(channel, media.file_id, caption=f"Forwarded: {file_name}")
                logging.info(f"File {file_name} forwarded to {channel}.")
            except Exception as e:
                logging.error(f"Error forwarding {file_name} to {channel}: {e}")

        sleep(2 * 60)  # Short delay between files

    processing = False  # Reset the processing flag


@Client.on_message(filters.document | filters.audio | filters.video)
async def handle_file(client, message):
    """Handles incoming media messages."""
    global processing

    if message.chat.id == MSYD:  # Ensure the file is from the specified chat
        try:
            file = getattr(message, message.media.value)  # Get the media object
            if not file:
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

            # Start processing the queue if not already running
            if not processing:
                processing = True
                await process_queue(client)

        except Exception as e:
            logging.error(f"Error handling file: {e}")
