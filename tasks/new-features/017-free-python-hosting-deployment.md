# Free Python Hosting and Deployment Infrastructure

**GitHub Issue**: #219 - https://github.com/bdperkin/nhl-scrabble/issues/219

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

8-12 hours

## Description

Configure free hosting infrastructure for the NHL Scrabble web interface with automated CI/CD deployment, GitHub integration, and optimized workflows for Python backends. This enables public access to the web application without hosting costs while maintaining professional deployment practices.

## Current State

The project currently has no web hosting infrastructure:

- CLI-only application (no web interface deployed)
- No hosting platform configured
- No CI/CD deployment pipeline
- No production environment setup
- All usage requires local installation

**Dependencies:**

- Web interface implementation (tasks/new-features/001-web-interface.md)
- May benefit from i18n/l10n (tasks/new-features/016-internationalization-localization.md)

## Proposed Solution

### Platform Evaluation

Research and select a free Python hosting platform that meets requirements:

#### Option 1: PythonAnywhere (Recommended for Flask/Django)

**Pros:**

- Free tier with persistent storage
- Direct GitHub pull integration
- Supports Flask, Django, web2py
- SSH access for debugging
- Scheduled tasks (cron jobs)
- MySQL/PostgreSQL databases included

**Cons:**

- Limited to 1 web app on free tier
- 100,000 daily requests limit
- No custom domain on free tier
- Manual deployment (or scheduled git pull)

**Configuration:**

```bash
# .pythonanywhere/setup.sh
#!/bin/bash

# Pull latest code
cd /home/username/nhl-scrabble
git pull origin main

# Update dependencies
source venv/bin/activate
uv pip install -r requirements.txt

# Reload web app
touch /var/www/username_pythonanywhere_com_wsgi.py
```

**WSGI Configuration:**

```python
# /var/www/username_pythonanywhere_com_wsgi.py
import sys
import os

# Add project directory to path
project_home = "/home/username/nhl-scrabble"
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ["NHL_SCRABBLE_ENV"] = "production"
os.environ["NHL_SCRABBLE_API_TIMEOUT"] = "15"

# Import Flask app
from src.nhl_scrabble.web.app import app as application
```

#### Option 2: Render (Recommended for Modern CI/CD)

**Pros:**

- Free tier with auto-deploy from GitHub
- Native Git integration (push to deploy)
- Supports Docker and buildpacks
- Custom domains on free tier
- Automatic HTTPS
- Better for CI/CD workflows

**Cons:**

- Free tier spins down after inactivity
- 750 hours/month limit
- Limited build minutes (400/month)
- PostgreSQL free tier is limited

**Configuration:**

```yaml
# render.yaml
services:
  - type: web
    name: nhl-scrabble
    env: python
    region: oregon
    plan: free
    branch: main
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn src.nhl_scrabble.web.app:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.14
      - key: NHL_SCRABBLE_ENV
        value: production
      - key: NHL_SCRABBLE_API_TIMEOUT
        value: 15
```

#### Option 3: Railway (Generous Free Tier)

**Pros:**

- $5 free credit per month
- Auto-deploy from GitHub
- Supports Docker
- PostgreSQL/Redis included
- Very fast deployments
- Good developer experience

**Cons:**

- Free tier limited to $5/month usage
- May run out mid-month under heavy usage
- Requires credit card for verification

**Configuration:**

```toml
# railway.toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "gunicorn src.nhl_scrabble.web.app:app --bind 0.0.0.0:$PORT"
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

#### Option 4: Fly.io (Docker-Based)

**Pros:**

- Free tier: 3 shared VMs, 3GB storage
- Excellent Docker support
- Global deployment (edge locations)
- Good for APIs and backends
- PostgreSQL included

**Cons:**

- Requires Docker knowledge
- More complex setup
- Free tier limited resources
- Credit card required

**Configuration:**

```toml
# fly.toml
app = "nhl-scrabble"
primary_region = "ewr"

[build]
dockerfile = "Dockerfile"

[env]
PORT = "8080"
NHL_SCRABBLE_ENV = "production"

[[services]]
http_checks = []
internal_port = 8080
processes = ["app"]
protocol = "tcp"
script_checks = []

[[services.ports]]
force_https = true
handlers = ["http"]
port = 80

[[services.ports]]
handlers = ["tls", "http"]
port = 443
```

### Recommended Choice: Render

**Rationale:**

- Best CI/CD integration (auto-deploy on git push)
- Free custom domains and HTTPS
- No manual deployment needed
- Good free tier for low-traffic apps
- Easy to upgrade if needed

### Implementation Architecture

```
GitHub Repository
       ↓
   (git push)
       ↓
GitHub Actions CI
  - Run tests
  - Run linting
  - Build Docker image
       ↓
   (on success)
       ↓
Render Deployment
  - Pull latest code
  - Install dependencies
  - Start Gunicorn
  - Serve Flask app
       ↓
   Public URL
  nhl-scrabble.onrender.com
```

### CI/CD Pipeline Configuration

**.github/workflows/deploy.yml:**

```yaml
name: Deploy to Render

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.14'

      - name: Install dependencies
        run: |
          pip install uv
          uv pip install -e ".[dev]"

      - name: Run tests
        run: pytest

      - name: Run linting
        run: ruff check .

      - name: Run type checking
        run: mypy src/

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Trigger Render Deploy
        run: |
          curl -X POST "${{ secrets.RENDER_DEPLOY_HOOK_URL }}"
```

### Environment Configuration

**Production Environment Variables:**

```bash
# .env.production (not committed, set in hosting platform)
NHL_SCRABBLE_ENV=production
NHL_SCRABBLE_API_TIMEOUT=15
NHL_SCRABBLE_API_RETRIES=5
NHL_SCRABBLE_RATE_LIMIT_DELAY=0.5
NHL_SCRABBLE_CACHE_ENABLED=true
NHL_SCRABBLE_CACHE_TTL=3600
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=<generate-random-secret>
```

**Configuration Loading:**

```python
# src/nhl_scrabble/web/config.py
import os
from pathlib import Path


class ProductionConfig:
    """Production configuration."""

    DEBUG = False
    TESTING = False

    # Load from environment
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable not set")

    # NHL Scrabble settings
    NHL_API_TIMEOUT = int(os.getenv("NHL_SCRABBLE_API_TIMEOUT", "15"))
    NHL_API_RETRIES = int(os.getenv("NHL_SCRABBLE_API_RETRIES", "5"))
    RATE_LIMIT_DELAY = float(os.getenv("NHL_SCRABBLE_RATE_LIMIT_DELAY", "0.5"))

    # Caching
    CACHE_ENABLED = os.getenv("NHL_SCRABBLE_CACHE_ENABLED", "true").lower() == "true"
    CACHE_TTL = int(os.getenv("NHL_SCRABBLE_CACHE_TTL", "3600"))


def get_config():
    """Get configuration based on environment."""
    env = os.getenv("NHL_SCRABBLE_ENV", "development")

    if env == "production":
        return ProductionConfig()
    elif env == "testing":
        return TestingConfig()
    else:
        return DevelopmentConfig()
```

### Web Server Configuration

**Gunicorn for Production:**

```python
# gunicorn.conf.py
import multiprocessing

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "nhl-scrabble"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
# keyfile = None
# certfile = None
```

**Run Command:**

```bash
gunicorn src.nhl_scrabble.web.app:app --config gunicorn.conf.py
```

### Health Check Endpoint

```python
# src/nhl_scrabble/web/app.py
from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/health")
def health_check():
    """Health check endpoint for deployment platforms."""
    return (
        jsonify(
            {
                "status": "healthy",
                "version": "2.0.0",
                "environment": os.getenv("NHL_SCRABBLE_ENV", "unknown"),
            }
        ),
        200,
    )


@app.route("/ready")
def readiness_check():
    """Readiness check - verify external dependencies."""
    try:
        # Test NHL API connectivity
        from nhl_scrabble.api import NHLApiClient

        with NHLApiClient() as client:
            client.get_teams()  # Quick test call

        return jsonify({"status": "ready", "nhl_api": "available"}), 200
    except Exception as e:
        return jsonify({"status": "not_ready", "error": str(e)}), 503
```

### Deployment Documentation

**README.deployment.md:**

````markdown
# Deployment Guide

## Platform: Render

### Initial Setup

1. Sign up for Render account
2. Connect GitHub repository
3. Create new Web Service
4. Configure build settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn src.nhl_scrabble.web.app:app --config gunicorn.conf.py`

### Environment Variables

Configure in Render dashboard:

- `NHL_SCRABBLE_ENV=production`
- `NHL_SCRABBLE_API_TIMEOUT=15`
- `SECRET_KEY=<random-secret>`

### Automatic Deployment

Push to main branch triggers automatic deployment:

```bash
git push origin main
````

Deployment status: https://dashboard.render.com/

### Manual Deployment

Trigger from Render dashboard or via deploy hook:

```bash
curl -X POST "$RENDER_DEPLOY_HOOK_URL"
```

### Monitoring

- Health check: https://nhl-scrabble.onrender.com/health
- Readiness: https://nhl-scrabble.onrender.com/ready
- Logs: Render dashboard

### Troubleshooting

**Deployment fails:**

- Check GitHub Actions CI passed
- Verify environment variables set
- Check Render build logs

**App crashes:**

- Check error logs in Render dashboard
- Verify all dependencies in requirements.txt
- Test locally with production config

**Slow response:**

- Free tier spins down after inactivity
- First request after sleep takes ~30s
- Consider paid tier for always-on

````

## Implementation Steps

1. **Choose Hosting Platform** (1h)

   - Research platforms (PythonAnywhere, Render, Railway, Fly.io)
   - Compare free tiers and features
   - Test deployment workflow
   - Document decision rationale
   - **Recommendation: Render** (best CI/CD integration)

2. **Configure Production Environment** (2h)

   - Create production configuration class
   - Set up environment variable loading
   - Generate SECRET_KEY
   - Configure gunicorn
   - Add health check endpoints
   - Test configuration locally

3. **Set Up CI/CD Pipeline** (2h)

   - Create `.github/workflows/deploy.yml`
   - Configure test stage (pytest, ruff, mypy)
   - Configure deployment stage
   - Set up deploy webhook/hook
   - Test pipeline with dummy deployment

4. **Initial Deployment** (1h)

   - Sign up for hosting platform
   - Connect GitHub repository
   - Configure build/start commands
   - Set environment variables
   - Trigger first deployment
   - Verify app is running

5. **Configure Monitoring** (1h)

   - Set up health check endpoint
   - Configure readiness check
   - Add logging configuration
   - Test monitoring endpoints
   - Document monitoring approach

6. **Optimize for Production** (2h)

   - Configure caching
   - Optimize gunicorn workers
   - Add request timeouts
   - Configure rate limiting
   - Test under load (basic)
   - Tune performance settings

7. **Documentation** (1-2h)

   - Create deployment guide
   - Document environment variables
   - Add troubleshooting section
   - Update README with deployment link
   - Document rollback procedure
   - Add monitoring guide

8. **Testing** (1h)

   - Test deployment from clean state
   - Verify CI/CD pipeline
   - Test health checks
   - Verify environment variables loaded
   - Test app functionality in production
   - Verify logs are accessible

## Testing Strategy

### Pre-Deployment Testing

```bash
# Test with production config locally
export NHL_SCRABBLE_ENV=production
export SECRET_KEY=test-secret

# Run gunicorn locally
gunicorn src.nhl_scrabble.web.app:app --config gunicorn.conf.py

# Test health endpoints
curl http://localhost:8000/health
curl http://localhost:8000/ready

# Load test (basic)
ab -n 1000 -c 10 http://localhost:8000/
````

### Deployment Testing

```bash
# Trigger deployment
git push origin main

# Wait for deployment
# Monitor GitHub Actions

# Test production endpoints
curl https://nhl-scrabble.onrender.com/health
curl https://nhl-scrabble.onrender.com/ready

# Test full application flow
curl https://nhl-scrabble.onrender.com/analyze
```

### Monitoring Validation

- ✅ Health check returns 200
- ✅ Readiness check verifies NHL API
- ✅ Logs are accessible
- ✅ Errors are logged properly
- ✅ Response times < 3s (first request after wake)
- ✅ Response times < 500ms (warm requests)

## Acceptance Criteria

- [ ] Hosting platform selected and documented
- [ ] Production configuration implemented
- [ ] Gunicorn configured for production
- [ ] Health check endpoint working
- [ ] Readiness check endpoint working
- [ ] CI/CD pipeline configured in GitHub Actions
- [ ] Automatic deployment on push to main
- [ ] Environment variables configured on hosting platform
- [ ] Initial deployment successful
- [ ] App accessible via public URL
- [ ] Logs accessible and working
- [ ] Deployment documentation complete (README.deployment.md)
- [ ] Troubleshooting guide created
- [ ] README.md updated with deployment link
- [ ] Monitoring endpoints tested
- [ ] Performance acceptable on free tier
- [ ] Rollback procedure documented
- [ ] All tests pass in production environment

## Related Files

**New Files:**

- `gunicorn.conf.py` - Gunicorn production configuration
- `.github/workflows/deploy.yml` - CI/CD deployment pipeline
- `src/nhl_scrabble/web/config.py` - Production configuration
- `README.deployment.md` - Deployment guide
- `render.yaml` - Render platform configuration (if using Render)
- `.env.production.example` - Example production environment variables

**Modified Files:**

- `src/nhl_scrabble/web/app.py` - Add health/readiness endpoints
- `README.md` - Add deployment link and badge
- `requirements.txt` - Add gunicorn
- `.gitignore` - Ignore `.env.production`

## Dependencies

**Task Dependencies:**

- tasks/new-features/001-web-interface.md - Web interface must exist first
- May benefit from tasks/new-features/016-internationalization-localization.md

**Package Dependencies:**

```toml
[project.dependencies]
# Existing dependencies...
gunicorn = ">=21.0.0" # Production WSGI server

[project.optional-dependencies.deploy]
# Deployment-specific dependencies
python-dotenv = ">=1.0.0" # Load environment variables
```

## Additional Notes

### Platform Comparison Summary

| Platform       | Free Tier              | CI/CD       | Custom Domain | Best For             |
| -------------- | ---------------------- | ----------- | ------------- | -------------------- |
| PythonAnywhere | 1 app, 100k req/day    | Manual/Cron | No            | Simple Flask/Django  |
| Render         | 750h/month, sleeps     | Auto-deploy | Yes           | **Recommended**      |
| Railway        | $5/month credit        | Auto-deploy | Yes           | Generous free tier   |
| Fly.io         | 3 VMs, 3GB             | Auto-deploy | Yes           | Docker enthusiasts   |
| Vercel         | Serverless limitations | Auto-deploy | Yes           | Next.js/static sites |

### Why Render is Recommended

1. **Best CI/CD**: Native GitHub integration, auto-deploy on push
1. **Free HTTPS**: Automatic SSL certificates
1. **Custom Domains**: Free custom domain support
1. **Easy Setup**: Minimal configuration required
1. **Good DX**: Excellent developer experience
1. **Upgrade Path**: Easy to upgrade to paid tier if needed

### Free Tier Limitations

**Render Free Tier:**

- Spins down after 15 minutes of inactivity
- First request after sleep: ~30 seconds cold start
- 750 hours/month (enough for single app)
- Limited build minutes: 400/month

**Workarounds:**

- Use cron job to ping health endpoint every 14 minutes
- Accept cold starts for low-traffic demo app
- Upgrade to paid tier ($7/month) for always-on

### Security Considerations

**Environment Variables:**

- Never commit `.env.production` to git
- Use platform's environment variable management
- Rotate SECRET_KEY periodically
- Use strong random secrets

**HTTPS:**

- All platforms provide free HTTPS
- Enforce HTTPS in production
- Set secure cookie flags

**Rate Limiting:**

- Implement rate limiting for API endpoints
- Prevent abuse on free tier
- Monitor request patterns

### Performance Optimization

**Caching:**

- Enable caching for NHL API responses
- Set appropriate cache TTL (1 hour recommended)
- Reduce API calls to stay within limits

**Gunicorn Workers:**

- Free tier: 2-4 workers recommended
- Formula: (2 × CPU) + 1
- Monitor memory usage

**Response Times:**

- Target: < 500ms for cached requests
- Cold start: ~30s acceptable for free tier
- First API call: 3-5s expected

### Cost Considerations

**Free Tier Sustainability:**

- Render free tier: Sustainable for low-traffic demo
- Monthly costs if upgraded: $7-25/month
- Alternative: Self-host on home server (free but requires effort)

**When to Upgrade:**

- Need always-on availability (no cold starts)
- Traffic exceeds 750 hours/month
- Need more than 512MB RAM
- Require faster build times

### Future Enhancements

After initial deployment:

- Add CDN for static assets (Cloudflare)
- Implement Redis caching (requires paid tier)
- Add application monitoring (Sentry, LogRocket)
- Set up custom domain
- Add CI/CD deployment notifications (Slack/Discord)
- Implement blue-green deployments

### Breaking Changes

None - this is new infrastructure, no existing deployment to break.

### Migration Path

If switching platforms in the future:

1. New platform uses same codebase (portable)
1. Environment variables portable across platforms
1. Gunicorn configuration universal
1. Docker option available (Dockerfile-based deployment)

### Alternative Approaches

**Self-Hosting:**

- Pros: Full control, no vendor lock-in, truly free
- Cons: Requires server maintenance, uptime responsibility, complexity

**Serverless:**

- Pros: Auto-scaling, pay-per-request, no cold starts (AWS Lambda warm)
- Cons: More complex setup, potential costs, vendor lock-in

**Container Platforms:**

- Pros: Portable, scalable, industry-standard
- Cons: More complex, often not free, requires Docker knowledge
