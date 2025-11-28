FROM alpine@sha256:115729ec5cb049ba6359c3ab005ac742012d92bbaa5b8bc1a878f1e8f62c0cb8

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apk add --no-cache \
    curl=8.17.0-r1 gnupg=2.4.8-r1 python3=3.12.12-r0 py3-pip=25.1.1-r1 unzip=6.0-r16 ca-certificates=20251003-r0 nano=8.7-r0

# Add Jellyfin repository and key
RUN sed -i 's/^#\(.*community.*\)/\1/' /etc/apk/repositories
RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories
RUN apk update

# Install jellyfin-ffmpeg6
RUN apk add --no-cache jellyfin-ffmpeg=7.1.2_p3-r0

# Install Intel Media Drivers
RUN apk add --no-cache intel-media-driver
RUN apk add onevpl-intel-gpu=25.3.4-r0 --repository=http://dl-cdn.alpinelinux.org/alpine/edge/

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
