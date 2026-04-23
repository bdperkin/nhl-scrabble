# How to Deploy the Web Interface

This guide explains how to deploy the NHL Scrabble web interface to production environments.

## Prerequisites

- Python 3.10+ installed
- NHL Scrabble package installed
- Production server or cloud platform
- Domain name (optional but recommended)
- Reverse proxy (nginx, Caddy, or Traefik recommended)

## Installation on Server

### 1. Install Package

```bash
# Clone repository
git clone https://github.com/bdperkin/nhl-scrabble.git
cd nhl-scrabble

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install with web dependencies
pip install -e ".[web]"

# Or using UV (faster)
uv pip install -e ".[web]"
```

### 2. Install Production Server

Install Gunicorn with uvicorn worker:

```bash
pip install gunicorn[setproctitle] uvicorn[standard]
```

Or using UV:

```bash
uv pip install gunicorn uvicorn[standard]
```

## Production Configuration

### Environment Variables

Create `.env` file:

```bash
# Server Configuration
NHL_SCRABBLE_WEB_HOST=0.0.0.0
NHL_SCRABBLE_WEB_PORT=8000
NHL_SCRABBLE_WEB_WORKERS=4

# CORS Configuration
NHL_SCRABBLE_CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# API Configuration
NHL_SCRABBLE_API_TIMEOUT=15
NHL_SCRABBLE_API_RETRIES=5
NHL_SCRABBLE_RATE_LIMIT_DELAY=0.3

# Cache Configuration
NHL_SCRABBLE_CACHE_TTL=3600  # 1 hour in seconds

# Logging
NHL_SCRABBLE_LOG_LEVEL=INFO
NHL_SCRABBLE_LOG_FORMAT=json
```

See [Environment Variables Reference](../reference/environment-variables.md) for all options.

### Gunicorn Configuration

Create `gunicorn.conf.py`:

```python
"""Gunicorn configuration for NHL Scrabble web interface."""

import multiprocessing

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2

# Logging
accesslog = "-"  # stdout
errorlog = "-"  # stderr
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "nhl-scrabble-web"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if not using reverse proxy)
keyfile = None
certfile = None
```

## Running in Production

### Using Gunicorn Directly

```bash
gunicorn nhl_scrabble.web.app:app \
    --config gunicorn.conf.py \
    --access-logfile - \
    --error-logfile -
```

### Using Systemd Service

Create `/etc/systemd/system/nhl-scrabble-web.service`:

```ini
[Unit]
Description=NHL Scrabble Web Interface
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/nhl-scrabble
Environment="PATH=/opt/nhl-scrabble/.venv/bin"
ExecStart=/opt/nhl-scrabble/.venv/bin/gunicorn \
    nhl_scrabble.web.app:app \
    --config /opt/nhl-scrabble/gunicorn.conf.py \
    --access-logfile - \
    --error-logfile -
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable nhl-scrabble-web
sudo systemctl start nhl-scrabble-web
sudo systemctl status nhl-scrabble-web
```

View logs:

```bash
sudo journalctl -u nhl-scrabble-web -f
```

## Reverse Proxy Configuration

### Nginx

Create `/etc/nginx/sites-available/nhl-scrabble`:

```nginx
upstream nhl_scrabble {
    server 127.0.0.1:8000 fail_timeout=0;
}

server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL configuration (use certbot for Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/yourdomain.com/chain.pem;

    # SSL security
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;  # codespell:ignore aNULL
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;

    # Client limits
    client_max_body_size 10M;
    client_body_timeout 60s;

    # Logging
    access_log /var/log/nginx/nhl-scrabble-access.log;
    error_log /var/log/nginx/nhl-scrabble-error.log;

    location / {
        proxy_pass http://nhl_scrabble;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Static files (optional caching)
    location /static {
        proxy_pass http://nhl_scrabble;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Health check (bypass logging)
    location /health {
        proxy_pass http://nhl_scrabble;
        access_log off;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/nhl-scrabble /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Caddy

Create `Caddyfile`:

```caddyfile
yourdomain.com {
    reverse_proxy localhost:8000

    encode gzip

    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "DENY"
        X-XSS-Protection "1; mode=block"
    }

    log {
        output file /var/log/caddy/nhl-scrabble.log
    }
}
```

Run Caddy:

```bash
sudo caddy run --config Caddyfile
```

## SSL/TLS Configuration

### Let's Encrypt with Certbot

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate (for nginx)
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Or for standalone
sudo certbot certonly --standalone -d yourdomain.com
```

Certbot automatically configures renewal via cron/systemd timer.

### Caddy (Automatic HTTPS)

Caddy automatically obtains and renews Let's Encrypt certificates - no configuration needed!

## Security Hardening

### 1. Update CORS Origins

Update `src/nhl_scrabble/web/app.py` or set environment variable:

```python
allow_origins = ["https://yourdomain.com", "https://www.yourdomain.com"]
```

Or via environment:

```bash
export NHL_SCRABBLE_CORS_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"
```

### 2. Add Rate Limiting

Install slowapi for rate limiting:

```bash
pip install slowapi
```

Update `app.py`:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/api/analyze")
@limiter.limit("10/minute")
async def analyze_get(request: Request):
    # Analysis logic here
    pass
```

### 3. Content Security Policy

Already configured in `SecurityHeadersMiddleware`. Adjust as needed for your domain.

### 4. Firewall Rules

```bash
# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Block direct access to app (only allow nginx)
sudo ufw deny 8000/tcp

sudo ufw enable
```

## Monitoring and Logging

### Application Logging

Configure structured logging in production:

```python
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "format": '{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
```

### Health Monitoring

Use `/health` endpoint for monitoring:

```bash
# Uptime monitoring
curl https://yourdomain.com/health

# Or use monitoring services like:
# - UptimeRobot
# - Pingdom
# - StatusCake
# - Datadog
```

### Performance Monitoring

Track API performance:

```python
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter("requests_total", "Total requests")
REQUEST_DURATION = Histogram("request_duration_seconds", "Request duration")
```

## Deployment Platforms

### Heroku

```bash
# Create Procfile
echo "web: gunicorn nhl_scrabble.web.app:app -k uvicorn.workers.UvicornWorker" > Procfile

# Deploy
heroku create nhl-scrabble
git push heroku main
heroku open
```

### DigitalOcean App Platform

Create `app.yaml`:

```yaml
name: nhl-scrabble
services:
  - name: web
    github:
      repo: yourusername/nhl-scrabble
      branch: main
    run_command: gunicorn nhl_scrabble.web.app:app -k
      uvicorn.workers.UvicornWorker
    http_port: 8000
    instance_count: 2
    instance_size_slug: basic-xs
    routes:
      - path: /
```

### Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Fly.io

Create `fly.toml`:

```toml
app = "nhl-scrabble"

[build]
builder = "paketobuildpacks/builder:base"

[[services]]
internal_port = 8000
protocol = "tcp"

[[services.ports]]
port = 80
handlers = ["http"]

[[services.ports]]
port = 443
handlers = ["tls", "http"]
```

Deploy:

```bash
flyctl launch
flyctl deploy
```

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[web]" gunicorn

# Copy application
COPY src/ ./src/

# Expose port
EXPOSE 8000

# Run with gunicorn
CMD ["gunicorn", "nhl_scrabble.web.app:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - 8000:8000
    environment:
      - NHL_SCRABBLE_LOG_LEVEL=INFO
    restart: unless-stopped
    healthcheck:
      test: [CMD, curl, -f, http://localhost:8000/health]
      interval: 30s
      timeout: 10s
      retries: 3
```

Build and run:

```bash
docker-compose up -d
docker-compose logs -f
```

## Troubleshooting

### Workers Timing Out

Increase timeout in `gunicorn.conf.py`:

```python
timeout = 60  # Increase from 30
```

### High Memory Usage

Reduce worker count:

```python
workers = 2  # Instead of CPU count * 2 + 1
```

### Slow First Request

Pre-warm cache on startup by making initial request to `/api/analyze`.

### CORS Errors

Verify CORS origins in configuration match your domain exactly (including https://).

## Performance Optimization

1. **Enable HTTP/2** in reverse proxy
1. **Use CDN** for static assets
1. **Enable compression** (gzip/brotli)
1. **Configure caching** headers for static files
1. **Use production ASGI server** (Gunicorn + Uvicorn)
1. **Scale horizontally** with multiple workers/instances

## Next Steps

- [Configure Monitoring](../explanation/monitoring.md)
- [Set Up CI/CD](../../.github/workflows/deploy.yml)
- [Performance Tuning](../how-to/optimize-performance.md)
- [Security Hardening](../../SECURITY.md)

## Related Documentation

- [Use Web Interface](use-web-interface.md)
- [Environment Variables](../reference/environment-variables.md)
- [Web Architecture](../explanation/web-architecture.md)
- [Contributing](../../CONTRIBUTING.md)
