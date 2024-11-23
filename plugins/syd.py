from pyrogram import Client, filters
from time import sleep
import os


if not os.path.exists("received_files"):
    os.makedirs("received_files")

CHANNELS = ["-1002464733363", "-1002429058090", "-1002433450358"]
file_queue = []
MSYD = -1002377676305
@Client.on_message(filters.document | filters.audio | filters.video)
def handle_file(client, message):
    if message.chat.id == MSYD:
        try:
           file_id = message.file_id
           file_name = message.document.file_name if message.document else "unknown_file"
           message.download(file_name=f"received_files/{file_name}")
           file_queue.append(file_id)

        except Exception as e:
            print(f"Error receiving file: {e}")




def forward_files():
  while True:
        if file_queue:
            # Forward up to 8 files, each to a different channel
            for i in range(min(8, len(file_queue))):
                # Pop the file from the queue
                file_id = file_queue.pop(0)

                # Send the file to the next channel in a round-robin fashion
                channel = CHANNELS[i % len(CHANNELS)]
                try:
                    app.send_document(channel, file_id)
                    print(f"File {file_id} forwarded to {channel}.")
                except Exception as e:
                    print(f"Error forwarding to {channel}: {e}")
            
            print("Batch of files forwarded. Waiting for 30 minutes...")
            sleep(30)  # Wait 30 minutes before the next batch
        else:
            print("No files in the queue. Checking again in 10 seconds...")
            sleep(10)
