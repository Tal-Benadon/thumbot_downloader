# ThumbBot Downloader - Complete Project Documentation

## 🎯 Project Overview

ThumbBot Downloader is a Python-based video downloading service that uses Cobalt API to download videos from various social media platforms (Instagram, YouTube, TikTok, Twitter, etc.) and upload them to Discord channels. The project has been refactored from yt-dlp to use Cobalt for better platform support and reliability.

## 🏗️ Architecture

### Core Components

1. **FastAPI Application** (`main.py`)
   - RESTful API server
   - Handles video download requests via HTTP endpoints

2. **Cobalt Integration** (`app/services/cobalt_client.py`)
   - Client for interacting with Cobalt API instances
   - Supports multiple instance fallbacks
   - Settings fallback system for quality/codec/format

3. **Download Service** (`app/services/downloader.py`)
   - Orchestrates the download process
   - Handles file size validation
   - Manages temporary files and cleanup

4. **Configuration System** (`app/config.py`)
   - Environment-based configuration
   - Support for MB-based file size limits
   - Fallback settings for video quality, codec, and audio format

5. **Discord Integration** (`app/api/discord.py`)
   - Uploads downloaded videos to Discord channels
   - Optional dependency (graceful degradation)

## 🔧 Current Status

### ✅ Working Features
- **Cobalt API Integration**: Successfully connects to Cobalt instances
- **Instance Fallbacks**: Tries multiple Cobalt instances if primary fails
- **Settings Fallbacks**: Automatic fallback for video quality, codec, and audio format
- **Configuration System**: Environment-based config with MB support
- **File Size Management**: Configurable limits with Discord tier support
- **Docker Support**: Self-hosted Cobalt instance via Docker Compose
- **Error Handling**: Comprehensive error handling and logging

### ⚠️ Known Issues
- **Parameter Compatibility**: Current Cobalt instance only accepts URL parameter
  - Extra parameters (`vQuality`, `vCodec`, `aFormat`) cause `invalid_body` error
  - Settings fallback system is implemented but disabled pending API research
- **Dependencies**: Some optional dependencies (python-dotenv) may be missing

### 🔬 Testing Status
- **Instagram Downloads**: ✅ Working (tested with real Instagram reel)
- **Configuration System**: ✅ Working (MB limits, fallbacks)
- **Docker Setup**: ✅ Working (Cobalt instance running on port 9000)
- **Fallback Systems**: ✅ Implemented (but parameters disabled due to API compatibility)

## 📁 Project Structure

```
thumbot_downloader/
├── app/                          # Main application package
│   ├── api/                      # API endpoints
│   │   ├── routes.py            # Route configuration
│   │   ├── videos.py            # Video download endpoints
│   │   └── discord.py           # Discord integration
│   ├── services/                 # Business logic
│   │   ├── cobalt_client.py     # Cobalt API client
│   │   └── downloader.py        # Download orchestration
│   ├── config.py                # Configuration management
│   └── exceptions.py            # Custom exceptions
├── docker-compose.cobalt.yml     # Cobalt Docker setup
├── requirements.txt             # Python dependencies (minimal)
├── requirements.txt.backup      # Original dependencies (backup)
├── env.example                  # Environment configuration template
├── manage_config.py             # Configuration management CLI
├── test_instagram_with_config.py # Test script
├── DOCKER_SETUP.md             # Docker setup instructions
├── COBALT_MIGRATION.md         # Migration documentation
└── PROJECT_DOCUMENTATION.md    # This file
```

## 🛠️ Setup Instructions

### 1. Environment Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
```bash
# Copy environment template
cp env.example .env

# Edit configuration
# Key settings:
# - COBALT_API_URL=http://localhost:9000
# - VIDEO_QUALITY=1080p
# - MAX_FILE_SIZE_MB=8.0
# - PICKER_BEHAVIOR=first
```

### 3. Docker Setup (Cobalt Instance)
```bash
# Start Cobalt Docker container
docker-compose -f docker-compose.cobalt.yml up -d

# Verify it's running
docker-compose -f docker-compose.cobalt.yml ps
curl http://localhost:9000/api/serverInfo
```

### 4. Testing
```bash
# Test configuration
python3 manage_config.py show
python3 manage_config.py test

# Test video download
python3 test_instagram_with_config.py
```

## ⚙️ Configuration Reference

### Environment Variables

#### Core Settings
- `COBALT_API_URL`: Cobalt instance URL (default: http://localhost:9000)
- `VIDEO_QUALITY`: Preferred video quality (1080p, 720p, 480p, etc.)
- `VIDEO_CODEC`: Preferred codec (h264, vp9, av1)
- `AUDIO_FORMAT`: Audio format (best, mp3, ogg, opus, wav)

#### File Size Management
- `MAX_FILE_SIZE_MB`: File size limit in MB (easier than bytes)
- `MAX_FILE_SIZE`: File size limit in bytes (alternative)
- `DISCORD_FILE_LIMIT`: Discord upload limit

#### Behavior Settings
- `PICKER_BEHAVIOR`: How to handle multiple files (first, last, all, best)
- `DISABLE_METADATA`: Strip metadata from files (true/false)
- `AUTO_CLEANUP`: Auto-delete files after upload (true/false)

#### Platform-Specific
- `TIKTOK_H265`: Allow H.265 for TikTok (better quality, worse compatibility)
- `TWITTER_GIF`: Convert Twitter loops to GIF
- `YOUTUBE_DUB_LANG`: YouTube dubbed language preference

### Fallback System

The configuration system includes automatic fallbacks:

**Quality Fallbacks**: 1080p → 720p → 480p → 360p → 240p
**Codec Fallbacks**: h264 → vp9 → av1
**Audio Fallbacks**: best → mp3 → ogg → opus → wav

This ensures downloads succeed even when preferred settings aren't available.

## 🔌 API Reference

### Main Endpoint
```
POST /api/videos/download
Content-Type: application/json

{
  "url": "https://www.instagram.com/reel/DMM205mSJTy/",
  "channel_id": "discord_channel_id"
}
```

### Configuration Management
```bash
# Show current configuration
python3 manage_config.py show

# Show available options
python3 manage_config.py options

# Test configuration
python3 manage_config.py test
```

## 🐳 Docker Integration

### Cobalt Instance
- **Image**: `ghcr.io/imputnet/cobalt:10`
- **Port**: 9000
- **Health Check**: Enabled
- **Configuration**: Production-ready with CORS enabled

### Docker Commands
```bash
# Start services
docker-compose -f docker-compose.cobalt.yml up -d

# Check status
docker-compose -f docker-compose.cobalt.yml ps

# View logs
docker-compose -f docker-compose.cobalt.yml logs cobalt-api

# Stop services
docker-compose -f docker-compose.cobalt.yml down
```

## 🔍 Troubleshooting

### Common Issues

1. **"invalid_body" Error**
   - Current Cobalt instance only accepts URL parameter
   - Extra parameters are disabled until API compatibility is resolved
   - Downloads still work, just without custom quality/codec settings

2. **Missing Dependencies**
   - Install: `pip install python-dotenv`
   - Or use minimal requirements.txt (recommended)

3. **Docker Container Not Responding**
   - Check if running: `docker-compose -f docker-compose.cobalt.yml ps`
   - Restart: `docker-compose -f docker-compose.cobalt.yml restart`

4. **File Size Errors**
   - Adjust `MAX_FILE_SIZE_MB` in environment
   - Check Discord server tier limits (8MB free, 25MB basic, 100MB nitro)

### Debug Commands
```bash
# Test Cobalt API directly
curl -X POST "http://localhost:9000/" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.instagram.com/reel/DMM205mSJTy/"}'

# Check configuration
python3 manage_config.py show

# Test with different settings
MAX_FILE_SIZE_MB=25 VIDEO_QUALITY=720p python3 manage_config.py test
```

## 🚀 Development Notes

### Code Quality
- Type hints throughout codebase
- Comprehensive error handling
- Logging for debugging
- Configuration validation

### Testing
- Test scripts included
- Configuration validation
- Real-world Instagram testing
- Docker integration testing

### Future Improvements
1. **Research Cobalt API Parameters**
   - Investigate correct parameter names for quality/codec settings
   - Enable settings fallback system once parameters are working

2. **Enhanced Platform Support**
   - Test with more platforms (YouTube, TikTok, Twitter)
   - Platform-specific optimizations

3. **Monitoring & Metrics**
   - Success/failure rates
   - Performance metrics
   - Instance health monitoring

## 📝 Migration History

- **From**: yt-dlp with provider-specific modules
- **To**: Cobalt API with unified interface
- **Benefits**: Better platform support, cleaner architecture, Docker deployment
- **Status**: Core functionality working, parameter system pending API research

## 🔗 Related Files

- `DOCKER_SETUP.md`: Detailed Docker setup instructions
- `COBALT_MIGRATION.md`: Migration process documentation
- `env.example`: Complete environment configuration template
- `requirements.txt.backup`: Original dependencies (if rollback needed)

---

*Last Updated: Current session*
*Status: Core functionality working, ready for development*