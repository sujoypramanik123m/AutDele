FROM python:3.10.6

# Update packages and install necessary tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        gnupg \
        dirmngr \
        wget

# Add the GPG key to verify the Debian repository
RUN wget -qO - https://ffmpeg.org/releases/ffmpeg-release.gpg.key | apt-key add -

# Add the official FFmpeg repository
RUN echo "deb http://www.deb-multimedia.org buster main" >> /etc/apt/sources.list.d/ffmpeg.list && \
    apt-get update

# Install FFmpeg (this will install the latest version available from the repository)
RUN apt-get install -y ffmpeg

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app/

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Command to run when the container starts
CMD ["bash", "run.sh"]
