FROM alpine@sha256:115729ec5cb049ba6359c3ab005ac742012d92bbaa5b8bc1a878f1e8f62c0cb8

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apk add \
    curl gnupg python3 py3-pip unzip ca-certificates nano

# Add Jellyfin repository and key
RUN sed -i 's/^#\(.*community.*\)/\1/' /etc/apk/repositories
RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories
RUN apk update

# Install jellyfin-ffmpeg6
RUN apk add --no-cache jellyfin-ffmpeg

# Install Intel Media Drivers
RUN apk add --no-cache intel-media-driver
RUN apk add onevpl-intel-gpu --repository=http://dl-cdn.alpinelinux.org/alpine/edge/

# Install JS library for yt-dlp
RUN curl -fsSL https://deno.land/install.sh | sh

# Symlink ffmpeg and ffprobe to PATH
RUN ln -s /usr/lib/jellyfin-ffmpeg/ffmpeg /usr/local/bin/ffmpeg \
 && ln -s /usr/lib/jellyfin-ffmpeg/ffprobe /usr/local/bin/ffprobe

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt --break-system-packages

# Copy Python script
COPY discordBot.py /app/

# Default command
CMD ["python3", "discordBot.py"]
