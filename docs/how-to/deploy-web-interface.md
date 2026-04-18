# Deploying the Web Interface

This guide covers deploying the NHL Scrabble web interface to production environments.

## Prerequisites

- Python 3.10 or higher
- NHL Scrabble package installed
- Production-grade ASGI server (Uvicorn recommended)
- (Optional) Reverse proxy (Nginx, Caddy, or Traefik)
- (Optional) Process manager (Systemd, Supervisor, or PM2)

## Quick Deployment (Development)

**Not recommended for production** - For testing only:

```bash
uvicorn nhl_scrabble.web.app:app --host 0.0.0.0 --port 8000
```

## Production Deployment

### Using Uvicorn with Workers

Uvicorn with multiple workers for production:

```bash
uvicorn nhl_scrabble.web.app:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level info \
  --access-log \
  --proxy-headers \
  --forwarded-allow-ips='*'
```

**Worker Count**: Set to number of CPU cores (e.g., 4 workers for 4-core machine).

### Using Gunicorn with Uvicorn Workers

For better process management:

```bash
gunicorn nhl_scrabble.web.app:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile - \
  --log-level info
```

Install Gunicorn first:

```bash
pip install gunicorn
```

## Environment Variables

Configure via environment variables or `.env` file:

```bash
# NHL API Settings
NHL_SCRABBLE_API_TIMEOUT=15
NHL_SCRABBLE_API_RETRIES=3
NHL_SCRABBLE_RATE_LIMIT_DELAY=0.3

# Caching
NHL_SCRABBLE_CACHE_ENABLED=true
NHL_SCRABBLE_CACHE_EXPIRY=3600  # 1 hour in seconds

# Logging
NHL_SCRABBLE_LOG_LEVEL=INFO
NHL_SCRABBLE_VERBOSE=false

# Performance
NHL_SCRABBLE_TOP_PLAYERS=20
NHL_SCRABBLE_TOP_TEAM_PLAYERS=5
```

See [Environment Variables Reference](../reference/environment-variables.md) for complete list.

## Reverse Proxy Configuration

### Nginx

```nginx
server {
    listen 80;
    server_name nhl-scrabble.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (if needed in future)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Static files (optional optimization)
    location /static {
        alias /path/to/nhl_scrabble/web/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### Caddy

```caddy
nhl-scrabble.example.com {
    reverse_proxy 127.0.0.1:8000
}
```

Caddy automatically handles HTTPS with Let's Encrypt.

### Traefik (Docker)

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    image: nhl-scrabble:latest
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.nhl.rule=Host(`nhl-scrabble.example.com`)"
      - "traefik.http.routers.nhl.entrypoints=websecure"
      - "traefik.http.routers.nhl.tls.certresolver=letsencrypt"
    environment:
      - NHL_SCRABBLE_CACHE_ENABLED=true
      - NHL_SCRABBLE_LOG_LEVEL=INFO
```

## Process Management

### Systemd (Linux)

Create `/etc/systemd/system/nhl-scrabble.service`:

```ini
[Unit]
Description=NHL Scrabble Web Interface
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/nhl-scrabble
Environment="PATH=/var/www/nhl-scrabble/.venv/bin"
ExecStart=/var/www/nhl-scrabble/.venv/bin/uvicorn \
  nhl_scrabble.web.app:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable nhl-scrabble
sudo systemctl start nhl-scrabble
sudo systemctl status nhl-scrabble
```

### Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml uv.lock ./
RUN pip install uv && \
    uv pip install --system -e .

# Copy application
COPY . .

# Run as non-root user
RUN useradd -m -u 1000 app && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Start application
CMD ["uvicorn", "nhl_scrabble.web.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t nhl-scrabble .
docker run -p 8000:8000 nhl-scrabble
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - NHL_SCRABBLE_CACHE_ENABLED=true
      - NHL_SCRABBLE_LOG_LEVEL=INFO
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Run with:

```bash
docker-compose up -d
```

## Security Considerations

### HTTPS/TLS

**Always use HTTPS in production.** Options:

1. **Let's Encrypt** (free): Use Certbot, Caddy, or Traefik
1. **Cloud provider**: Use AWS ACM, Google Cloud SSL, etc.
1. **Self-signed** (testing only): Not recommended for production

### Security Headers

Security headers are automatically configured:

```text
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self'; ...
```

These are set by `SecurityHeadersMiddleware` in the FastAPI app.

### CORS Configuration

Update CORS settings in `app.py` for production:

```python
# For production, specify exact origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://nhl-scrabble.example.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

Current configuration allows localhost only (development).

### Rate Limiting

**Not currently implemented** - Consider adding rate limiting for production:

1. **Application level**: Use `slowapi` library
1. **Reverse proxy**: Use Nginx `limit_req` module
1. **Cloud level**: Use AWS WAF, Cloudflare, etc.

See [issue #XXX] for planned rate limiting feature.

### Environment Variables

**Never commit secrets** to version control:

- Use `.env` file (already in `.gitignore`)
- Use environment variable management (AWS Secrets Manager, HashiCorp Vault)
- Use container orchestration secrets (Docker secrets, Kubernetes secrets)

## Monitoring & Logging

### Health Check Endpoint

The `/health` endpoint returns server status:

```json
{
  "status": "healthy",
  "version": "2.0.0",
  "timestamp": "2026-04-17T12:00:00.000Z"
}
```

Use for:

- Load balancer health checks
- Container orchestration health probes
- Uptime monitoring services

### Application Logs

Logs are written to stdout/stderr by default:

```bash
# View logs (systemd)
journalctl -u nhl-scrabble -f

# View logs (Docker)
docker logs -f nhl-scrabble

# View logs (Docker Compose)
docker-compose logs -f web
```

Configure log level via `NHL_SCRABBLE_LOG_LEVEL` environment variable.

### Metrics (Future)

Currently not implemented. Planned features:

- Prometheus metrics endpoint
- Request duration histograms
- Cache hit/miss ratios
- NHL API call statistics

## Performance Tuning

### Caching

Enable aggressive caching for production:

```bash
NHL_SCRABBLE_CACHE_ENABLED=true
NHL_SCRABBLE_CACHE_EXPIRY=3600  # 1 hour
```

Cache is in-memory (per worker). For shared cache, consider Redis (future enhancement).

### Worker Count

Recommended worker counts:

- **CPU-bound**: 2-4 workers per CPU core
- **I/O-bound** (this app): 2 workers per CPU core
- **Minimum**: 2 workers for redundancy
- **Maximum**: 2 × CPU cores

### Static Files

For better performance:

1. Serve static files directly from Nginx/Caddy
1. Use CDN for static assets (future enhancement)
1. Enable compression (gzip/brotli) in reverse proxy

## Scaling

### Horizontal Scaling

For high traffic:

1. Run multiple instances behind load balancer
1. Use shared cache (Redis) instead of in-memory
1. Consider async NHL API calls with connection pooling

### Vertical Scaling

For single instance:

1. Increase worker count (2 × CPU cores)
1. Increase system resources (RAM, CPU)
1. Enable caching with longer expiry

## Troubleshooting

See [Troubleshooting Guide](troubleshooting-web.md) for common deployment issues.

## Production Checklist

Before deploying to production:

- [ ] HTTPS/TLS configured
- [ ] Security headers verified
- [ ] CORS configured for production domains
- [ ] Environment variables configured
- [ ] Logging configured and tested
- [ ] Health check endpoint working
- [ ] Process manager configured
- [ ] Reverse proxy configured
- [ ] Static files served efficiently
- [ ] Caching enabled and tested
- [ ] Rate limiting configured (recommended)
- [ ] Monitoring/alerting set up
- [ ] Backup/disaster recovery plan
- [ ] Documentation updated

## Next Steps

- Set up monitoring with Prometheus/Grafana
- Add rate limiting for API endpoints
- Implement Redis-based shared cache
- Add metrics dashboard
- Configure alerting for errors/downtime
