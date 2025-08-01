# Docker Setup for ThumbBot with Cobalt

This guide will help you set up a self-hosted Cobalt instance using Docker to work with your ThumbBot downloader.

## Quick Start

1. **Start the Cobalt service:**
   ```bash
   docker-compose -f docker-compose.cobalt.yml up -d
   ```

2. **Verify Cobalt is running:**
   ```bash
   curl http://localhost:9000/api/serverInfo
   ```

3. **Test your ThumbBot integration:**
   ```bash
   python3 -c "
   from app.services.downloader import proccess_video_request
   result = proccess_video_request('https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'test_channel')
   print(result)
   "
   ```

## Detailed Setup

### Prerequisites

- Docker and Docker Compose installed
- Your ThumbBot project (already set up)

### Step 1: Start Cobalt Service

The `docker-compose.cobalt.yml` file contains a pre-configured Cobalt instance:

```bash
# Start Cobalt in the background
docker-compose -f docker-compose.cobalt.yml up -d

# Check if it's running
docker-compose -f docker-compose.cobalt.yml ps

# View logs
docker-compose -f docker-compose.cobalt.yml logs -f cobalt-api
```

### Step 2: Configuration

The Cobalt instance is configured with:

- **Port**: 9000 (http://localhost:9000)
- **CORS**: Enabled for local development
- **Rate Limiting**: 20 requests per minute
- **File Size Limit**: 128MB
- **Duration Limit**: 3 hours

You can modify these settings in the `docker-compose.cobalt.yml` file.

### Step 3: Environment Variables

Create a `.env` file or use the provided `docker.env`:

```bash
# Copy the example
cp docker.env .env

# Edit with your configuration
nano .env
```

### Step 4: Test the Setup

#### Test Cobalt directly:
```bash
# Check server info
curl http://localhost:9000/api/serverInfo

# Test video download (returns JSON with download info)
curl -X POST http://localhost:9000/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"url":"https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

#### Test ThumbBot integration:
```bash
# Make sure your Python dependencies are installed
pip install -r requirements.txt

# Test the integration
python3 test_local_cobalt.py
```

## Configuration Options

### Cobalt Environment Variables

You can customize the Cobalt instance by modifying the environment variables in `docker-compose.cobalt.yml`:

- `API_PORT`: Port for the API (default: 9000)
- `API_URL`: Public URL for the instance
- `API_NAME`: Instance name
- `CORS_WILDCARD`: Enable CORS (1 = enabled)
- `DURATION_LIMIT`: Max video duration in seconds
- `FILE_SIZE_LIMIT`: Max file size in MB
- `RATE_LIMIT`: Requests per window
- `RATE_LIMIT_WINDOW`: Rate limit window in seconds

### ThumbBot Configuration

Your ThumbBot will automatically use the local Cobalt instance. You can override this by setting:

```bash
export COBALT_API_URL="http://localhost:9000"
```

## Troubleshooting

### Cobalt not starting:
```bash
# Check logs
docker-compose -f docker-compose.cobalt.yml logs cobalt-api

# Restart the service
docker-compose -f docker-compose.cobalt.yml restart cobalt-api
```

### Connection refused:
```bash
# Make sure Cobalt is running
docker-compose -f docker-compose.cobalt.yml ps

# Check if port 9000 is available
netstat -tuln | grep 9000
```

### API errors:
```bash
# Check Cobalt health
curl http://localhost:9000/api/serverInfo

# Test with a simple video
curl -X POST http://localhost:9000/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"url":"https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

## Production Considerations

For production use, consider:

1. **Reverse Proxy**: Use nginx or traefik
2. **SSL/TLS**: Enable HTTPS
3. **Resource Limits**: Adjust CPU/memory limits
4. **Monitoring**: Add health checks and monitoring
5. **Backups**: Cobalt is stateless, but consider logging

## Stopping the Service

```bash
# Stop Cobalt
docker-compose -f docker-compose.cobalt.yml down

# Stop and remove volumes (if any)
docker-compose -f docker-compose.cobalt.yml down -v
```

## Advanced Usage

### Using Multiple Cobalt Instances

You can run multiple Cobalt instances for load balancing:

```bash
# Scale to 3 instances
docker-compose -f docker-compose.cobalt.yml up -d --scale cobalt-api=3
```

### Custom Configuration

Create a custom docker-compose override:

```yaml
# docker-compose.override.yml
services:
  cobalt-api:
    environment:
      - DURATION_LIMIT=7200  # 2 hours instead of 3
      - FILE_SIZE_LIMIT=64   # 64MB instead of 128MB
```

Then run:
```bash
docker-compose -f docker-compose.cobalt.yml -f docker-compose.override.yml up -d
```