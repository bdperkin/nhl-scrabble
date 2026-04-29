# Performance and Load Testing

This directory contains performance and load tests for the NHL Scrabble web application.

## Overview

Performance testing measures how fast the application responds under normal conditions, while load testing measures behavior under concurrent user loads.

## Test Types

### 1. Page Load Tests (`test_page_load.py`)

Measures page load times and ensures they meet performance thresholds.

- **Threshold**: 2 seconds per page
- **Pages tested**: Homepage, Teams, Divisions, Conferences, Playoffs, Stats
- **Method**: Playwright with time measurement

**Run page load tests:**

```bash
pytest qa/web/tests/performance/test_page_load.py -v
```

**Run with performance marker:**

```bash
pytest -m performance qa/web/tests/performance/test_page_load.py -v
```

### 2. Response Time Tests (`test_response_time.py`)

Measures API response times and page rendering performance.

- **API Response Threshold**: 1 second
- **Render Time Threshold**: 0.5 seconds
- **Method**: HTTP requests and Playwright navigation timing

**Run response time tests:**

```bash
pytest qa/web/tests/performance/test_response_time.py -v
```

### 3. Benchmark Tests

Uses `pytest-benchmark` to create performance baselines and track regressions.

**Run benchmark tests:**

```bash
pytest -m benchmark qa/web/tests/performance/ -v
```

**Compare benchmarks:**

```bash
# Run and save baseline
pytest -m benchmark --benchmark-save=baseline

# Run and compare against baseline
pytest -m benchmark --benchmark-compare=baseline

# View benchmark results
pytest -m benchmark --benchmark-histogram
```

### 4. Load Tests (`locustfile.py`)

Simulates concurrent users accessing the application using Locust.

**User types:**

- `WebsiteUser`: Typical user (1-3s between requests, balanced page access)
- `HeavyUser`: Power user (0.5-1.5s between requests, aggressive browsing)
- `CasualUser`: Casual visitor (3-10s between requests, mainly homepage)

## Running Load Tests

### Quick Start

```bash
# Start the web application first
make serve  # or: uvicorn src.nhl_scrabble.web.app:app

# In another terminal, run load test
locust -f qa/web/tests/performance/locustfile.py \
       --host http://localhost:5000
```

Then open http://localhost:8089 in your browser to:

- Set number of users
- Set spawn rate
- Start/stop tests
- View real-time statistics
- View response time graphs

### Headless Load Testing

For CI/CD or automated testing:

```bash
# 50 users, 5/s spawn rate, 2 minute duration
locust -f qa/web/tests/performance/locustfile.py \
       --host http://localhost:5000 \
       --users 50 \
       --spawn-rate 5 \
       --run-time 2m \
       --headless

# With CSV output for analysis
locust -f qa/web/tests/performance/locustfile.py \
       --host http://localhost:5000 \
       --users 100 \
       --spawn-rate 10 \
       --run-time 5m \
       --headless \
       --csv qa/web/tests/performance/results/load_test_$(date +%Y%m%d_%H%M%S)
```

### Testing Specific User Types

```bash
# Test with only WebsiteUser (typical users)
locust -f qa/web/tests/performance/locustfile.py \
       --host http://localhost:5000 \
       --user-classes WebsiteUser \
       --users 30

# Test with only HeavyUser (stress test)
locust -f qa/web/tests/performance/locustfile.py \
       --host http://localhost:5000 \
       --user-classes HeavyUser \
       --users 20

# Test with only CasualUser (realistic load)
locust -f qa/web/tests/performance/locustfile.py \
       --host http://localhost:5000 \
       --user-classes CasualUser \
       --users 50

# Test with mixed user types (default)
locust -f qa/web/tests/performance/locustfile.py \
       --host http://localhost:5000 \
       --users 60  # Will be distributed across all user classes
```

### Custom Load Test Scenarios

**Spike Test** (sudden traffic spike):

```bash
locust -f qa/web/tests/performance/locustfile.py \
       --host http://localhost:5000 \
       --users 200 \
       --spawn-rate 50 \
       --run-time 2m \
       --headless
```

**Endurance Test** (sustained load):

```bash
locust -f qa/web/tests/performance/locustfile.py \
       --host http://localhost:5000 \
       --users 50 \
       --spawn-rate 5 \
       --run-time 30m \
       --headless
```

**Capacity Test** (find maximum users):

```bash
# Start with low users, monitor response times, increase gradually
locust -f qa/web/tests/performance/locustfile.py \
       --host http://localhost:5000 \
       --users 500 \
       --spawn-rate 25 \
       --run-time 10m \
       --headless
```

## Performance Thresholds

| Metric            | Threshold | Notes                                             |
| ----------------- | --------- | ------------------------------------------------- |
| Page Load Time    | < 2.0s    | All pages should load within 2 seconds            |
| API Response Time | < 1.0s    | API endpoints should respond within 1 second      |
| Render Time       | < 0.5s    | Page rendering should complete within 0.5 seconds |
| Fast Page Load    | < 1.0s    | Ideal target for all pages                        |

## Interpreting Results

### Page Load Tests

```
PASSED test_homepage_load_time (0.85s)
```

- ✅ Page loaded in 0.85s (under 2s threshold)

```
FAILED test_teams_page_load_time - AssertionError: Teams page loaded in 2.34s (threshold: 2.0s)
```

- ❌ Page load time exceeded threshold (optimization needed)

### Load Test Results

**Good Performance:**

- Average response time: < 500ms
- 95th percentile: < 1000ms
- 99th percentile: < 2000ms
- Failure rate: < 1%
- Requests per second: Stable

**Poor Performance:**

- Average response time: > 1000ms
- 95th percentile: > 2000ms
- Failure rate: > 5%
- Response times increasing over time (memory leak?)

### Benchmark Results

```
Name                          Min      Max     Mean    Median
test_homepage_load         734.21  1234.56   892.45   876.34
test_api_response           98.45   234.67   145.23   142.11
```

- Track changes over time
- Flag regressions (>10% slower)
- Celebrate improvements (>10% faster)

## CI/CD Integration

Add performance tests to CI pipeline:

```yaml
- name: Run Performance Tests
  run: |
    # Start application
    uvicorn src.nhl_scrabble.web.app:app &
    APP_PID=$!

    # Wait for application to start
    sleep 5

    # Run performance tests
    pytest qa/web/tests/performance/ -m performance -v

    # Run load test (headless, 2 minutes)
    locust -f qa/web/tests/performance/locustfile.py \
           --host http://localhost:5000 \
           --users 50 \
           --spawn-rate 5 \
           --run-time 2m \
           --headless

    # Stop application
    kill $APP_PID
```

## Troubleshooting

### Tests Failing Due to Slow Load Times

1. Check if application is running: `curl http://localhost:5000`
1. Check system resources: `top` or `htop`
1. Run tests individually to isolate slow pages
1. Increase thresholds temporarily to baseline current performance
1. Profile application to find bottlenecks

### Locust Not Found

```bash
# Install Locust
pip install locust

# Or install QA dependencies
pip install -e ".[qa]"
```

### Connection Refused

```bash
# Ensure application is running
uvicorn src.nhl_scrabble.web.app:app

# Or use make command
make serve
```

### High Failure Rate in Load Tests

1. Check application logs for errors
1. Reduce number of concurrent users
1. Increase spawn rate delay
1. Check database connection pool size
1. Monitor server resources (CPU, memory, network)

## Best Practices

1. **Run on isolated environment**: Performance tests should run on dedicated hardware/VM
1. **Consistent conditions**: Run tests under same conditions (time of day, network, hardware)
1. **Baseline first**: Establish baseline before making changes
1. **Monitor trends**: Track performance over time, not just pass/fail
1. **Load test before production**: Always load test before major releases
1. **Set realistic thresholds**: Base thresholds on actual user requirements
1. **Test various scenarios**: Mix user types, traffic patterns, durations

## Resources

- [Locust Documentation](https://docs.locust.io/)
- [pytest-benchmark Documentation](https://pytest-benchmark.readthedocs.io/)
- [Playwright Performance](https://playwright.dev/python/docs/test-timeouts)

## Results and Reports

Performance test results are stored in:

- **Benchmark results**: `.benchmarks/` (git-ignored)
- **Load test CSV**: `qa/web/tests/performance/results/` (git-ignored)
- **Reports**: `qa/web/tests/performance/reports/` (git-ignored)

Keep historical results for trend analysis and regression detection.
