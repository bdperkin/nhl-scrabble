# Troubleshooting the Web Interface

This guide covers common issues and solutions for the NHL Scrabble web interface.

## Server Won't Start

### Issue: `ModuleNotFoundError: No module named 'nhl_scrabble'`

**Cause**: Package not installed or wrong Python environment.

**Solution**:

```bash
# Verify you're in the right environment
which python

# Install package in editable mode
pip install -e .

# Or with UV
uv pip install -e .
```

### Issue: `Address already in use`

**Cause**: Port 8000 is already occupied.

**Solution**:

```bash
# Option 1: Use a different port
uvicorn nhl_scrabble.web.app:app --port 8001

# Option 2: Kill the process using port 8000
lsof -ti:8000 | xargs kill -9

# Option 3: Find and stop the conflicting process
lsof -i:8000
```

### Issue: `Permission denied` on port 80 or 443

**Cause**: Ports below 1024 require root privileges.

**Solution**:

```bash
# Option 1: Use a higher port (recommended)
uvicorn nhl_scrabble.web.app:app --port 8000

# Option 2: Use authbind (Linux)
authbind --deep uvicorn nhl_scrabble.web.app:app --port 80

# Option 3: Run behind reverse proxy (best for production)
# Let Nginx/Caddy handle port 80/443
```

## Static Files Not Loading

### Issue: 404 errors for CSS/JS files

**Cause**: Static files directory not found or not mounted.

**Solution**:

```bash
# Verify static directory exists
ls -la src/nhl_scrabble/web/static/

# Should contain:
# static/css/style.css
# static/js/app.js
```

If files are missing, they may not have been installed. Reinstall package:

```bash
pip install -e .
```

### Issue: CSS/JS files load but styles/scripts don't apply

**Cause**: Browser caching old files.

**Solution**:

```bash
# Hard refresh browser
# - Chrome/Firefox: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
# - Safari: Cmd+Option+R

# Or disable cache in DevTools
# Chrome DevTools -> Network tab -> Disable cache checkbox
```

## Templates Not Rendering

### Issue: "Templates not configured" message

**Cause**: Templates directory not found.

**Solution**:

```bash
# Verify templates directory exists
ls -la src/nhl_scrabble/web/templates/

# Should contain:
# base.html
# index.html
# results.html
```

### Issue: Template rendering errors

**Cause**: Jinja2 syntax errors in templates.

**Solution**:

Check server logs for specific error:

```bash
# Look for TemplateSyntaxError in logs
uvicorn nhl_scrabble.web.app:app --log-level debug
```

## API Endpoint Issues

### Issue: `/api/analyze` times out

**Cause**: NHL API is slow or unavailable.

**Solution**:

```bash
# Option 1: Enable caching (fastest)
# Call: /api/analyze?use_cache=true

# Option 2: Increase timeout
# Set environment variable:
export NHL_SCRABBLE_API_TIMEOUT=30

# Option 3: Check NHL API status manually
curl https://api-web.nhle.com/v1/standings/now
```

### Issue: `/api/analyze` returns 500 error

**Cause**: NHL API error or configuration issue.

**Solution**:

```bash
# Check server logs for specific error
uvicorn nhl_scrabble.web.app:app --log-level debug

# Common issues:
# 1. Network connectivity
ping api-web.nhle.com

# 2. Firewall blocking outbound requests
# Check firewall rules

# 3. Invalid configuration
# Verify environment variables
env | grep NHL_SCRABBLE
```

### Issue: `/api/analyze` returns 422 error

**Cause**: Invalid query parameters.

**Solution**:

Valid parameter ranges:

- `top_players`: 1-100
- `top_team_players`: 1-30
- `use_cache`: true/false

Example valid request:

```
/api/analyze?top_players=20&top_team_players=5&use_cache=true
```

## Performance Issues

### Issue: Slow initial load

**Cause**: First request fetches from NHL API (30-60 seconds).

**Solution**:

```bash
# Enable caching (subsequent requests will be fast)
/api/analyze?use_cache=true

# Pre-warm cache by running analysis once
curl "http://localhost:8000/api/analyze?use_cache=true"
```

### Issue: Slow even with caching enabled

**Cause**: Cache expired or not being used.

**Solution**:

```bash
# Check cache settings
env | grep NHL_SCRABBLE_CACHE

# Increase cache expiry (default 3600 seconds = 1 hour)
export NHL_SCRABBLE_CACHE_EXPIRY=7200  # 2 hours

# Verify caching is working (check logs)
uvicorn nhl_scrabble.web.app:app --log-level debug
# Look for "Cache hit" messages
```

### Issue: High memory usage

**Cause**: Too many workers or large cache.

**Solution**:

```bash
# Reduce worker count
uvicorn nhl_scrabble.web.app:app --workers 2

# Monitor memory usage
htop  # or top

# Restart server to clear cache
# (Cache is in-memory per worker)
```

## Browser Issues

### Issue: Form submission doesn't work

**Cause**: JavaScript not loading or errors.

**Solution**:

```bash
# Open browser DevTools (F12)
# Check Console tab for JavaScript errors

# Common issues:
# 1. JavaScript file not loaded (check Network tab)
# 2. JavaScript syntax error (check Console)
# 3. CORS error (check Console)
```

### Issue: Results don't display

**Cause**: JavaScript error or API error.

**Solution**:

```bash
# Check browser Console (F12) for errors
# Check Network tab for failed API requests

# Look for:
# - 500 errors: Server issue (check server logs)
# - 422 errors: Invalid parameters
# - CORS errors: CORS configuration issue
```

### Issue: Mobile layout broken

**Cause**: CSS not loading or viewport meta tag missing.

**Solution**:

Verify viewport meta tag in `base.html`:

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

Check CSS media queries are working:

```bash
# Open DevTools -> Toggle device toolbar
# Test different screen sizes
```

## Security Issues

### Issue: CORS errors in browser console

**Cause**: Accessing from different origin than configured.

**Solution**:

Update CORS configuration in `src/nhl_scrabble/web/app.py`:

```python
# Add your origin to allowed list
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://your-domain.com",  # Add your domain
    ],
    ...,
)
```

### Issue: CSP (Content Security Policy) blocking resources

**Cause**: Strict CSP in security headers.

**Solution**:

Check browser Console for CSP violations. Update CSP in `SecurityHeadersMiddleware` if needed:

```python
# Relax CSP for specific resources
response.headers["Content-Security-Policy"] = (
    "default-src 'self'; "
    "style-src 'self' 'unsafe-inline'; "
    "script-src 'self' 'unsafe-inline'"  # Necessary for inline scripts
)
```

### Issue: Mixed content warnings (HTTP/HTTPS)

**Cause**: Loading HTTP resources on HTTPS page.

**Solution**:

Ensure all resources use HTTPS or relative URLs:

```html
<!-- Bad -->
<script src="http://example.com/script.js"></script>

<!-- Good -->
<script src="https://example.com/script.js"></script>
<script src="/static/js/app.js"></script>
```

## Docker Issues

### Issue: Container exits immediately

**Cause**: Command error or missing dependencies.

**Solution**:

```bash
# Check container logs
docker logs nhl-scrabble

# Run container interactively for debugging
docker run -it nhl-scrabble /bin/bash

# Inside container, try running command manually
uvicorn nhl_scrabble.web.app:app --host 0.0.0.0
```

### Issue: Can't access container from host

**Cause**: Port mapping issue or host binding.

**Solution**:

```bash
# Verify port mapping
docker ps

# Ensure app binds to 0.0.0.0, not 127.0.0.1
# In Dockerfile CMD:
CMD ["uvicorn", "nhl_scrabble.web.app:app", "--host", "0.0.0.0"]

# Check firewall
sudo ufw status
```

## Logging Issues

### Issue: No logs appearing

**Cause**: Log level too high or logs going to wrong location.

**Solution**:

```bash
# Lower log level
export NHL_SCRABBLE_LOG_LEVEL=DEBUG
uvicorn nhl_scrabble.web.app:app --log-level debug

# Logs go to stdout/stderr by default
# Redirect to file if needed:
uvicorn nhl_scrabble.web.app:app > app.log 2>&1
```

### Issue: Too many logs

**Cause**: Debug level in production.

**Solution**:

```bash
# Use INFO level for production
export NHL_SCRABBLE_LOG_LEVEL=INFO
uvicorn nhl_scrabble.web.app:app --log-level info
```

## Health Check Issues

### Issue: `/health` endpoint returns 404

**Cause**: Endpoint not registered or routing issue.

**Solution**:

```bash
# Verify endpoint exists in app.py
grep -A5 "@app.get\(\"/health\"\)" src/nhl_scrabble/web/app.py

# Test directly
curl http://localhost:8000/health
```

### Issue: `/health` returns 500 error

**Cause**: Error in health check handler.

**Solution**:

```bash
# Check server logs for traceback
uvicorn nhl_scrabble.web.app:app --log-level debug

# Test the function directly
python -c "from nhl_scrabble.web.app import app; print(app)"
```

## Getting Help

If you're still stuck:

1. **Check server logs** with `--log-level debug`
1. **Check browser console** (F12) for client-side errors
1. **Search existing issues**: https://github.com/bdperkin/nhl-scrabble/issues
1. **Create a new issue**: Include:
   - Error message/traceback
   - Server logs
   - Browser console output
   - Environment details (OS, Python version)
   - Steps to reproduce

## Common Error Messages

### `NHLApiError: Failed to fetch standings`

**Meaning**: NHL API is down or unreachable.

**Fix**: Wait and retry, or check NHL API status.

### `HTTPException: 422 Unprocessable Entity`

**Meaning**: Invalid request parameters.

**Fix**: Check parameter ranges (see `/docs` endpoint).

### `RuntimeError: asyncio.run() cannot be called from a running event loop`

**Meaning**: Trying to run sync code in async context.

**Fix**: Use `await` for async functions, or use `asyncio.create_task()`.

### `TemplateNotFound: index.html`

**Meaning**: Template directory not configured correctly.

**Fix**: Verify templates directory exists and is readable.

### `StaticFilesNotFound`

**Meaning**: Static files directory not mounted.

**Fix**: Verify static directory exists and is readable.

## Prevention Best Practices

1. **Use environment variables** for configuration (don't hardcode)
1. **Enable caching** for production to reduce NHL API load
1. **Monitor health endpoint** with uptime monitoring service
1. **Test in staging** environment before production deployment
1. **Keep logs** for debugging (but rotate to prevent disk fill)
1. **Set up alerts** for 500 errors and timeouts
1. **Document custom configurations** for team members
1. **Regular updates** to dependencies for security patches

## Additional Resources

- [User Guide](use-web-interface.md) - Basic usage
- [Deployment Guide](deploy-web-interface.md) - Production setup
- [Environment Variables](../reference/environment-variables.md) - Configuration
- [API Documentation](http://localhost:8000/docs) - Interactive API docs
- [GitHub Issues](https://github.com/bdperkin/nhl-scrabble/issues) - Bug reports
