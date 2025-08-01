# 🔄 ThumbBot Downloader Service

Python FastAPI service that handles media download requests, coordinates with Cobalt for media extraction, and uploads files directly to Discord.

## 🎯 Service Overview

- **REST API** for video/media download processing
- **Cobalt Integration** for media extraction from platforms
- **Discord Integration** for direct file uploads
- **Multi-file Handling** with configurable picker behavior
- **File Management** with automatic cleanup and size validation

**Technology Stack:** FastAPI (Python 3.11+), requests, loguru, prometheus-client

## 📡 API Documentation

### Base URL
- Local: `http://localhost:8001`
- Docker: `http://thumbbot-downloader:8001`

### `POST /videos` - Download and Process Media

**Request:**
```json
{
  "url": "string",
  "channelId": "string"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Video processed and uploaded successfully"
}
```

**Examples:**

*YouTube Video:*
```bash
curl -X POST http://localhost:8001/videos \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "channelId": "1234567890123456789"
  }'
```

*Instagram Album (3 images):*
```bash
curl -X POST http://localhost:8001/videos \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.instagram.com/p/DMsrx6ysS-v/",
    "channelId": "1234567890123456789"
  }'
```

*TikTok Video:*
```bash
curl -X POST http://localhost:8001/videos \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.tiktok.com/@user/video/1234567890",
    "channelId": "1234567890123456789"
  }'
```

### `GET /health` - Health Check
```bash
curl http://localhost:8001/health
# Response: {"status": "healthy"}
```

## ⚙️ Features & Configuration

### Picker Behavior
Controls multi-file content handling:

| Behavior | Description | Example |
|----------|-------------|---------|
| `all` | Download all files, upload in single message | Instagram album → All 3 images |
| `first` | Download only the first file | Instagram album → First image only |
| `last` | Download only the last file | Instagram album → Last image only |

### File Format Support
- **Videos:** MP4, WebM, AVI (720p/1080p quality)
- **Images:** JPEG, PNG, WebP, GIF (original quality)
- **Audio:** MP3, OGG, WAV, Opus

### Discord Integration
- Direct Discord API uploads
- Multi-file messages (up to 10 files)
- 8MB file size limit (free Discord)
- Original filename preservation

## 🔧 Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `DISCORD_TOKEN` | *(required)* | Discord bot token |
| `COBALT_API_URL` | `http://thumbbot-cobalt:9000` | Cobalt instance URL |
| `PICKER_BEHAVIOR` | `all` | Multi-file behavior: all/first/last |
| `LOG_LEVEL` | `INFO` | Logging level |
| `MAX_FILE_SIZE_MB` | `8.0` | Maximum file size |
| `VIDEO_QUALITY` | `720` | Video quality: 144/360/720/1080/max |
| `VIDEO_CODEC` | `h264` | Video codec: h264/av1/vp9 |
| `AUDIO_FORMAT` | `best` | Audio format: best/mp3/ogg/wav/opus |
| `REQUEST_TIMEOUT` | `30` | HTTP request timeout (seconds) |
| `AUTO_CLEANUP` | `true` | Enable automatic file cleanup |

## 🛠️ Development Setup

### Local Development
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp ../env.example .env
# Edit .env: DISCORD_TOKEN=your_token_here

# Start development server
python main.py
```

### Start Cobalt (Required)
```bash
# Using Docker
docker run -p 9000:9000 ghcr.io/imputnet/cobalt:10
```

### Testing
```bash
# Run all tests
python -m pytest tests/ -v --cov=app

# Run specific tests
python -m pytest tests/test_api.py -v
```

## 🏗️ Code Structure
```
thumbot_downloader/
├── main.py                 # FastAPI app entry
├── app/
│   ├── api/
│   │   ├── routes.py       # API routes
│   │   ├── videos.py       # Video endpoints
│   │   └── discord.py      # Discord integration
│   ├── services/
│   │   ├── cobalt_client.py    # Cobalt API client
│   │   └── downloader.py       # Download logic
│   ├── utils/
│   │   ├── logger.py       # Logging config
│   │   └── metrics.py      # Prometheus metrics
│   └── config.py           # Configuration
├── tests/                  # Test suite
└── requirements.txt        # Dependencies
```

## 🚨 Error Handling

| Status | Error Type | Description |
|--------|------------|-------------|
| 200 | Success | Request processed successfully |
| 400 | Bad Request | Invalid URL or parameters |
| 413 | Too Large | File exceeds size limits |
| 500 | Server Error | Unexpected error |
| 502 | Bad Gateway | Cobalt unavailable |

**Error Response:**
```json
{
  "Error": "Descriptive error message",
  "request_id": "uuid-string",
  "timestamp": "2025-01-08T12:00:00Z"
}
```

## 📊 Request Flow Examples

### Instagram Album (3 images)
1. **Request:** `POST /videos` with Instagram URL
2. **Cobalt API:** Returns picker with 3 image URLs
3. **Download:** Downloads all 3 image files 
4. **Upload:** Uploads all files in single Discord message
5. **Cleanup:** Removes temporary files
6. **Response:** Success confirmation

### YouTube Video
1. **Request:** `POST /videos` with YouTube URL
2. **Cobalt API:** Returns direct video URL
3. **Download:** Downloads single MP4 file
4. **Upload:** Uploads file to Discord
5. **Cleanup:** Removes temporary file
6. **Response:** Success confirmation

## 📈 Monitoring

- **Metrics:** `http://localhost:8002/metrics` (Prometheus)
- **Health:** `http://localhost:8001/health`
- **Logs:** Structured JSON output with emojis

## 🔗 Related Documentation

- **[Main System](../README.md)** - Complete system overview
- **[Bot Service](../thumbot_bot/README.md)** - Discord bot integration
- **[Architecture](../ARCHITECTURE.md)** - System design details