def forward_files(app):
    """Forward files from the queue to channels at 30-minute intervals."""
    while True:
        if file_queue:
            for i in range(min(8, len(file_queue))):  # Process up to 8 files
                file_id = file_queue.pop(0)  # Remove the first file from the queue

                # Round-robin logic for channel selection
                channel = CHANNELS[i % len(CHANNELS)]
                try:
                    app.send_document(channel, file_id)  # Forward the file
                    print(f"File {file_id} forwarded to {channel}.")
                except Exception as e:
                    print(f"Error forwarding to {channel}: {e}")

            print("Batch of files forwarded. Waiting for 30 minutes...")
            sleep(30 * 60)  # Wait 30 minutes for the next batch
        else:
            print("No files in the queue. Checking again in 10 seconds...")
            sleep(10)  #
