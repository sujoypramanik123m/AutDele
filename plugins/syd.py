from pyrogram import Client, filters
from time import sleep
import os


if not os.path.exists("received_files"):
    os.makedirs("received_files")

CHANNELS = ["", "", ""]
file_queue = []

@Client.on_message(filters.document | filters.audio | filters.video)
def handle_file(client, message):
    if message.chat.id == MSYD:
        try:
           file_id = message.file_id
           file_name = message.document.file_name if message.document else "unknown_file"
           message.download(file_name=f"received_files/{file_name}")
           file_queue.append(file_id)



def forward_files():
  while True:
        if file_queue:
            # Forward up to 8 files
            for _ in range(min(8, len(file_queue))):
                file_id = file_queue.pop(0)  # Get the first file in the queue
                for channel in CHANNELS:
                    try:
                        app.send_document(channel, file_id)
                    except Exception as e:
                        print(f"Error forwarding to {channel}: {e}")
            print("Files forwarded. Waiting for 30 minutes...")
            sleep(30 * 60)  # 30 minutes interval
        else:
            sleep(10)
