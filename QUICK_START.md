# ThumbBot Downloader - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Setup Environment
```bash
# Clone and navigate to project
cd thumbot_downloader

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start Cobalt Docker Instance
```bash
# Start the Cobalt API service
docker-compose -f docker-compose.cobalt.yml up -d

# Verify it's working
curl -X POST "http://localhost:9000/" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.instagram.com/reel/DMM205mSJTy/"}'
```

### 3. Test Video Download
```bash
# Test Instagram download
python3 test_instagram_with_config.py

# Or test configuration
python3 manage_config.py show
python3 manage_config.py test
```

## ⚙️ Key Configuration

### Environment Variables (Optional)
```bash
# Create .env file from template
cp env.example .env

# Key settings:
MAX_FILE_SIZE_MB=8.0        # Discord file size limit
VIDEO_QUALITY=1080p         # Preferred quality
COBALT_API_URL=http://localhost:9000
```

### File Size Limits by Discord Tier
- **Free**: 8MB (`MAX_FILE_SIZE_MB=8.0`)
- **Nitro Basic**: 25MB (`MAX_FILE_SIZE_MB=25.0`)  
- **Nitro**: 100MB (`MAX_FILE_SIZE_MB=100.0`)

## 🔧 Current Status

### ✅ What Works
- Instagram video downloads
- Configuration system with MB limits
- Docker-based Cobalt instance
- Fallback system (implemented)
- File size validation

### ⚠️ Known Limitations
- Only URL parameter works with current Cobalt version
- Quality/codec parameters disabled (cause API errors)
- Settings fallback system ready but not active

## 🛠️ Common Commands

```bash
# Show current configuration
python3 manage_config.py show

# Test with different settings
MAX_FILE_SIZE_MB=25 VIDEO_QUALITY=720p python3 manage_config.py show

# Check Docker status
docker-compose -f docker-compose.cobalt.yml ps

# View Docker logs
docker-compose -f docker-compose.cobalt.yml logs cobalt-api

# Test API directly
curl -X POST "http://localhost:9000/" \
  -H "Content-Type: application/json" \
  -d '{"url":"PASTE_VIDEO_URL_HERE"}'
```

## 📁 Key Files

- `PROJECT_DOCUMENTATION.md` - Complete documentation
- `app/config.py` - Configuration system
- `app/services/cobalt_client.py` - Cobalt API client
- `manage_config.py` - Configuration management tool
- `docker-compose.cobalt.yml` - Cobalt Docker setup

## 🆘 Quick Troubleshooting

**Problem**: Downloads fail with "invalid_body"
**Solution**: This is expected - only URL parameter works currently

**Problem**: Docker container not responding  
**Solution**: `docker-compose -f docker-compose.cobalt.yml restart`

**Problem**: File too large errors
**Solution**: Adjust `MAX_FILE_SIZE_MB` in environment or .env file

**Problem**: Missing python-dotenv
**Solution**: `pip install python-dotenv` (optional dependency)

---

**Ready to develop!** 🎉 
See `PROJECT_DOCUMENTATION.md` for complete details.