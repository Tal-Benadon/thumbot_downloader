# ThumbBot - Downloader Service

This is the video downloader component of the ThumbBot microservices architecture. ThumbBot automatically downloads and shares videos from various social media platforms when links are posted in Discord channels.

## About This Repository

This repository contains the video downloader service written in Python/FastAPI. It's responsible for:

- Receiving video download requests from the ThumbBot Discord Bot Service
- Downloading videos from supported platforms (Reddit, Instagram, Facebook, etc.)
- Processing and optimizing videos for Discord upload size limits
- Providing API endpoints for the bot service to interact with

## Microservices Architecture

ThumbBot is available in two versions:

1. **Monolithic Version**: A single application combining bot and downloader functionality
   - [ThumbBot Monolithic Repository](https://github.com/Tal-Benadon/Thumbot)

2. **Microservices Version** (this repository): Two separate services that work together
   - **Bot Service**: Written in Node.js, handles Discord interactions
     - [ThumbBot Discord Service Repository](https://github.com/Tal-Benadon/thumbot_bot)
   - **Downloader Service** (this repository): Written in Python, handles video downloading and processing

The microservices architecture provides several advantages:
- Independent scaling of each component
- Ability to update components separately
- Improved resilience and fault isolation

## Project Structure

- `main.py`: FastAPI application entry point
- `app/api/`: API endpoint definitions
  - `routes.py`: Router configuration
  - `videos.py`: Video processing endpoints
  - `discord.py`: Discord communication utilities
- `app/services/`: Core service logic
  - `downloader.py`: Video downloading and processing logic
  - `providers_formats_processors/`: Provider-specific handling logic

## Features

- RESTful API for video download requests
- Supports multiple video providers including:
  - Reddit
  - Instagram Reels
  - Facebook videos and reels
- Handles size limitations (Discord's 8MB limit) and format conversions
- Intelligent format selection based on quality and size constraints

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Required Python packages (listed in requirements.txt)
- FFmpeg (for video processing)
- Discord Bot Token (required for uploading files to Discord)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/Tal-Benadon/thumbot_downloader.git
   cd thumbot_downloader
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Install FFmpeg (required for video processing):
   ```
   # Ubuntu/Debian
   sudo apt-get update && sudo apt-get install -y ffmpeg libsm6 libxext6 libxrender-dev libglib2.0-0
   
   # macOS (with Homebrew)
   brew install ffmpeg
   
   # Windows
   # Download from https://ffmpeg.org/download.html and add to your PATH
   ```

4. Create a directory for temporary video storage:
   ```
   mkdir temp_videos
   ```

5. Create a `.env` file with your Discord bot token:
   ```
   DISCORD_TOKEN=your_discord_bot_token_here
   ```

### Running the Service

Start the FastAPI server:
```
uvicorn main:app --reload
```

By default, the service will run on http://127.0.0.1:8000

### Docker Support

You can also run the service using Docker:

1. Build the Docker image:
   ```
   docker build -t thumbot-downloader .
   ```

   Note: Make sure your Dockerfile starts with `FROM python:3.10` (not python:3.10-slim) to ensure all necessary dependencies for FFmpeg are available.

2. Run the container:
   ```
   docker run -d --name thumbot-downloader \
     -p 8000:8000 \
     -e DISCORD_TOKEN=your_discord_bot_token_here \
     thumbot-downloader
   ```

Note: The Dockerfile must use a non-slim Python base image (`python:3.10` instead of `python:3.10-slim`) and install all necessary FFmpeg dependencies to ensure proper video processing.

### Alternative Token Configuration

Instead of using a `.env` file, you can directly set the bot token:

1. Direct environment variable (for development):
   ```
   export DISCORD_TOKEN=your_discord_bot_token_here
   uvicorn main:app --reload
   ```

2. In docker-compose.yml (for production):
   ```yaml
   services:
     bot:
       build: ./thumbot_bot
       environment:
         - DISCORD_TOKEN=your_actual_token_here  # Directly paste your token here
       # ...

     downloader:
       build: ./thumbot_downloader
       environment:
         - DISCORD_TOKEN=your_actual_token_here  # Directly paste your token here
       # ...
   ```

3. In Docker run command:
   ```
   docker run -d --name thumbot-downloader \
     -p 8000:8000 \
     -e DISCORD_TOKEN=your_actual_token_here \
     thumbot-downloader
   ```

Warning: Be careful with hardcoded tokens in configuration files. Never commit these files to public repositories.

### API Endpoints

- `GET /`: Health check endpoint
- `POST /videos`: Submit a video download request
  - Request body: `{ "url": "video_url", "channelId": "discord_channel_id" }`

## Using with Docker Compose

For running both the bot and downloader services together:

1. Create a `docker-compose.yml` file in a parent directory:

```yaml
version: '3'

services:
  bot:
    build: ./thumbot_bot
    environment:
      - DISCORD_TOKEN=${DISCORD_TOKEN}
    depends_on:
      - downloader
    restart: unless-stopped
    networks:
      - thumbot-network

  downloader:
    build: ./thumbot_downloader
    environment:
      - DISCORD_TOKEN=${DISCORD_TOKEN}  # Important: The downloader needs the Discord token for uploads
    ports:
      - "8000:8000"
    restart: unless-stopped
    volumes:
      - video_temp:/app/temp_videos
    networks:
      - thumbot-network

networks:
  thumbot-network:
    driver: bridge

volumes:
  video_temp:
```

2. Run both services with:
```
docker-compose up -d
```

Note: Make sure the `.env` file in your project root contains your Discord bot token, which will be used by both services.

Important: For Docker Compose to work properly, you need to:
1. Clone both repositories (thumbot_bot and thumbot_downloader) into the same parent directory
2. Place the docker-compose.yml file in that parent directory

For example:
```
parent-directory/
├── docker-compose.yml
├── thumbot_bot/
└── thumbot_downloader/
```

Important: Ensure the Dockerfile in thumbot_downloader starts with `FROM python:3.10` (not python:3.10-slim) to avoid FFmpeg installation issues. If you experience video processing errors, this is the first thing to check.

## Video Provider Support

Currently supported video providers:
- Reddit
- Instagram Reels
- Facebook videos and reels

You can customize which providers are supported by editing the providers configuration.

## Troubleshooting

- Some providers have rate limits that might affect downloading capacity
- Maximum file size for Discord uploads is 8MB for non-boosted servers
- For Docker setups, ensure the container has enough resources allocated for video processing
- FFmpeg installation issues can cause video processing failures

## Service Communication

The downloader and bot services communicate through a REST API:

1. The bot service makes HTTP requests to the downloader service endpoints.

2. Both services require access to the same Discord bot token:
   - The bot service uses it to connect to Discord and monitor messages
   - The downloader service uses it to upload processed videos directly to Discord through the `discord.py` module

3. The workflow is as follows:
   - Bot receives a message containing a video URL
   - Bot sends the URL to the downloader service via API
   - Downloader processes the video and uploads it directly to Discord using the bot token
   - Bot receives notification that the process is complete

4. If you experience issues:
   - Check that both services have the correct DISCORD_TOKEN
   - Verify that FFmpeg is properly installed (errors will appear in logs)
   - Ensure volume mounts are properly configured for temporary video storage

## License

See the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 