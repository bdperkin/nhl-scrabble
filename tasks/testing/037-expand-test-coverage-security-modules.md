# Expand Test Coverage of Security Modules

**GitHub Issue**: [#590](https://github.com/bdperkin/nhl-scrabble/issues/590)

## Priority

**HIGH** - Must Do (Next Sprint)

## Estimated Effort

12-16 hours

## Description

**Security-critical modules have dangerously low test coverage**, leaving the application vulnerable to security issues. Current coverage for security modules is **25.00%**, with **~122 untested statements** across 4 critical security subsystems:

- **circuit_breaker.py**: 27.06% (46 of 69 statements untested)
- **dos_protection.py**: 16.13% (18 of 23 statements untested)
- **log_filter.py**: 24.39% (19 of 29 statements untested)
- **ssrf_protection.py**: 21.43% (39 of 54 statements untested)

**Total missing coverage**: ~122 statements across 4 security modules

**⚠️ SECURITY CRITICAL**: These modules protect against:
- **SSRF** (Server-Side Request Forgery) attacks
- **DoS** (Denial of Service) attacks
- **Circuit breaker failures** and cascading outages
- **Secret/PII leakage** in logs

Low test coverage in security modules represents **HIGH RISK** to application security and stability.

## Current State

### Existing Tests (Partial Coverage):

**tests/unit/test_security.py** - EXISTS but only 25% coverage
- Basic tests exist but many code paths untested
- Missing edge case and attack scenario testing

**tests/integration/test_config_security.py** - Integration tests
- Exists but doesn't fully cover security module functionality

### Coverage Breakdown by Module:

**circuit_breaker.py (69 statements, 27.06% coverage):**
```
Lines missing: 81-94, 98-102, 106-123, 147-172, 195-201, 223, 243
Features untested:
- Circuit breaker state transitions (CLOSED → OPEN → HALF_OPEN)
- Failure threshold detection
- Success threshold for recovery
- Timeout handling
- State persistence
- Concurrent request handling
- Reset logic
- Metrics tracking
- Callback execution
```

**dos_protection.py (23 statements, 16.13% coverage):**
```
Lines missing: 44-79
Features untested:
- Connection limiting (max connections per host)
- Connection pool management
- Circuit breaker integration
- Request throttling
- Concurrent connection tracking
- Resource exhaustion prevention
- Error handling
```

**log_filter.py (29 statements, 24.39% coverage):**
```
Lines missing: 47-59, 218-226, 279-292
Features untested:
- Secret pattern detection (API keys, tokens, passwords)
- PII redaction (email, SSN, credit cards)
- Custom pattern filtering
- Redaction formatting
- Filter chaining
- Performance optimization
- Edge case handling
```

**ssrf_protection.py (54 statements, 21.43% coverage):**
```
Lines missing: 114-121, 150-166, 211-265, 299-305
Features untested:
- Private IP detection (192.168.x.x, 10.x.x.x, 127.0.0.1)
- Localhost detection
- IPv6 private address detection
- DNS rebinding protection
- URL parsing and validation
- Protocol validation (http/https only)
- Port blacklisting
- Hostname blacklisting
- Exception handling
```

## Proposed Solution

### 1. Comprehensive Security Testing Strategy

Create comprehensive test suites for each security module with focus on:
- **Attack scenarios** and exploit attempts
- **Edge cases** and boundary conditions
- **Concurrent access** and race conditions
- **Performance under load**
- **Integration** between security modules

#### A. Circuit Breaker (Priority 1 - Stability Critical)

**circuit_breaker.py** (46 untested statements):
```python
# tests/unit/test_circuit_breaker.py (enhance)
class TestCircuitBreaker:
    """Comprehensive circuit breaker tests."""

    def test_circuit_breaker_initialization(self):
        """Test circuit breaker starts in CLOSED state."""
        cb = CircuitBreaker(
            failure_threshold=5,
            timeout=60,
            success_threshold=2
        )
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0

    def test_state_transition_closed_to_open(self):
        """Test CLOSED → OPEN transition after failures."""
        cb = CircuitBreaker(failure_threshold=3)

        # Simulate failures
        for _ in range(3):
            try:
                with cb:
                    raise Exception("Simulated failure")
            except:
                pass

        assert cb.state == CircuitState.OPEN
        assert cb.failure_count == 3

    def test_state_transition_open_to_half_open(self):
        """Test OPEN → HALF_OPEN transition after timeout."""
        cb = CircuitBreaker(failure_threshold=1, timeout=0.1)

        # Trigger OPEN state
        try:
            with cb:
                raise Exception("Fail")
        except:
            pass

        assert cb.state == CircuitState.OPEN

        # Wait for timeout
        time.sleep(0.2)

        # Next call should transition to HALF_OPEN
        try:
            with cb:
                pass  # Success
        except:
            pass

        # Should be HALF_OPEN or CLOSED depending on success

    def test_state_transition_half_open_to_closed(self):
        """Test HALF_OPEN → CLOSED after successful requests."""
        cb = CircuitBreaker(
            failure_threshold=2,
            success_threshold=3,
            timeout=0.1
        )

        # Force OPEN state
        for _ in range(2):
            try:
                with cb:
                    raise Exception("Fail")
            except:
                pass

        time.sleep(0.2)

        # Send successful requests in HALF_OPEN
        for _ in range(3):
            with cb:
                pass  # Success

        assert cb.state == CircuitState.CLOSED

    def test_circuit_breaker_blocks_requests_when_open(self):
        """Test circuit breaker blocks requests in OPEN state."""
        cb = CircuitBreaker(failure_threshold=1)

        # Trigger OPEN
        try:
            with cb:
                raise Exception("Fail")
        except:
            pass

        # Should block immediately
        with pytest.raises(CircuitBreakerOpenError):
            with cb:
                pass

    def test_failure_threshold_detection(self):
        """Test accurate failure threshold tracking."""
        cb = CircuitBreaker(failure_threshold=5)

        # 4 failures - should stay CLOSED
        for _ in range(4):
            try:
                with cb:
                    raise Exception("Fail")
            except:
                pass

        assert cb.state == CircuitState.CLOSED

        # 5th failure - should transition to OPEN
        try:
            with cb:
                raise Exception("Fail")
        except:
            pass

        assert cb.state == CircuitState.OPEN

    def test_concurrent_request_handling(self):
        """Test circuit breaker with concurrent requests."""
        cb = CircuitBreaker(failure_threshold=10)

        def make_request(should_fail):
            try:
                with cb:
                    if should_fail:
                        raise Exception("Fail")
                    return "success"
            except:
                return "blocked or failed"

        # Concurrent execution
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(make_request, i % 2 == 0)
                for i in range(20)
            ]
            results = [f.result() for f in futures]

        # Verify concurrent safety

    def test_reset_logic(self):
        """Test manual circuit breaker reset."""
        cb = CircuitBreaker(failure_threshold=1)

        # Trigger OPEN
        try:
            with cb:
                raise Exception("Fail")
        except:
            pass

        assert cb.state == CircuitState.OPEN

        # Reset
        cb.reset()

        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0

    def test_metrics_tracking(self):
        """Test circuit breaker metrics."""
        cb = CircuitBreaker(failure_threshold=5)

        # Generate metrics
        for i in range(10):
            try:
                with cb:
                    if i % 3 == 0:
                        raise Exception("Fail")
            except:
                pass

        metrics = cb.get_metrics()
        assert "total_requests" in metrics
        assert "failures" in metrics
        assert "successes" in metrics

    def test_callback_execution(self):
        """Test state change callbacks."""
        state_changes = []

        def on_state_change(old_state, new_state):
            state_changes.append((old_state, new_state))

        cb = CircuitBreaker(
            failure_threshold=1,
            on_state_change=on_state_change
        )

        # Trigger state change
        try:
            with cb:
                raise Exception("Fail")
        except:
            pass

        assert len(state_changes) > 0
        assert state_changes[0][1] == CircuitState.OPEN

    # Cover all 46 untested statements
```

#### B. DoS Protection (Priority 1 - Security Critical)

**dos_protection.py** (18 untested statements):
```python
# tests/unit/test_dos_protection.py (create new)
class TestDosProtection:
    """DoS protection mechanism tests."""

    def test_connection_limiting(self):
        """Test max connections per host enforcement."""
        dos = DosProtection(
            max_connections=5,
            max_per_host=2
        )

        # Should allow first 2 connections from same host
        conn1 = dos.acquire_connection("192.168.1.1")
        conn2 = dos.acquire_connection("192.168.1.1")

        # Should block 3rd connection from same host
        with pytest.raises(DosProtectionError):
            dos.acquire_connection("192.168.1.1")

    def test_connection_pool_management(self):
        """Test connection pool lifecycle."""
        dos = DosProtection(max_connections=10)

        # Acquire connections
        connections = [
            dos.acquire_connection(f"host{i}")
            for i in range(10)
        ]

        # Pool should be full
        assert dos.is_pool_full()

        # Release connections
        for conn in connections:
            dos.release_connection(conn)

        # Pool should be empty
        assert not dos.is_pool_full()

    def test_circuit_breaker_integration(self):
        """Test integration with circuit breaker."""
        dos = DosProtection(
            max_connections=5,
            circuit_breaker_threshold=3
        )

        # Trigger circuit breaker
        for _ in range(3):
            try:
                dos.simulate_failure()
            except:
                pass

        # Should block new connections
        with pytest.raises(CircuitBreakerOpenError):
            dos.acquire_connection("test_host")

    def test_request_throttling(self):
        """Test request rate throttling."""
        dos = DosProtection(
            max_requests_per_second=10
        )

        # Send requests rapidly
        start = time.time()
        for _ in range(15):
            dos.check_rate_limit()
        duration = time.time() - start

        # Should take at least 0.5 seconds (throttled)
        assert duration >= 0.5

    def test_concurrent_connection_tracking(self):
        """Test thread-safe concurrent connection tracking."""
        dos = DosProtection(max_connections=20)

        def acquire_release():
            conn = dos.acquire_connection("test_host")
            time.sleep(0.01)
            dos.release_connection(conn)

        # Concurrent acquire/release
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(acquire_release)
                for _ in range(50)
            ]
            for f in futures:
                f.result()

        # All connections should be released
        assert dos.active_connections == 0

    def test_resource_exhaustion_prevention(self):
        """Test prevention of resource exhaustion attacks."""
        dos = DosProtection(
            max_connections=100,
            max_per_host=10,
            timeout=0.1
        )

        # Simulate attack from single host
        connections = []
        for _ in range(10):
            connections.append(dos.acquire_connection("attacker_ip"))

        # Should block further connections
        with pytest.raises(DosProtectionError, match="per-host limit"):
            dos.acquire_connection("attacker_ip")

        # Legitimate users should still be able to connect
        legit_conn = dos.acquire_connection("legit_user_ip")
        assert legit_conn is not None

    # Cover all 18 untested statements
```

#### C. Log Filter (Priority 1 - Data Protection)

**log_filter.py** (19 untested statements):
```python
# tests/unit/test_log_filter.py (create new)
class TestLogFilter:
    """Log filtering and secret redaction tests."""

    def test_api_key_detection(self):
        """Test API key pattern detection."""
        filter = LogFilter()

        log_message = "Connecting with API key: sk_live_1234567890abcdef"
        filtered = filter.filter(log_message)

        assert "sk_live_1234567890abcdef" not in filtered
        assert "[REDACTED_API_KEY]" in filtered

    def test_password_redaction(self):
        """Test password redaction."""
        filter = LogFilter()

        log_message = "Authentication failed for password='MySecretP@ss123'"
        filtered = filter.filter(log_message)

        assert "MySecretP@ss123" not in filtered
        assert "[REDACTED_PASSWORD]" in filtered

    def test_token_redaction(self):
        """Test OAuth/JWT token redaction."""
        filter = LogFilter()

        log_message = "Bearer token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        filtered = filter.filter(log_message)

        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in filtered
        assert "[REDACTED_TOKEN]" in filtered

    def test_email_pii_redaction(self):
        """Test email PII redaction."""
        filter = LogFilter(redact_pii=True)

        log_message = "User email: john.doe@example.com registered"
        filtered = filter.filter(log_message)

        assert "john.doe@example.com" not in filtered
        assert "[REDACTED_EMAIL]" in filtered

    def test_ssn_redaction(self):
        """Test SSN redaction."""
        filter = LogFilter(redact_pii=True)

        log_message = "SSN: 123-45-6789 verification failed"
        filtered = filter.filter(log_message)

        assert "123-45-6789" not in filtered
        assert "[REDACTED_SSN]" in filtered

    def test_credit_card_redaction(self):
        """Test credit card number redaction."""
        filter = LogFilter(redact_pii=True)

        log_message = "Payment failed for card 4532-1234-5678-9010"
        filtered = filter.filter(log_message)

        assert "4532-1234-5678-9010" not in filtered
        assert "[REDACTED_CREDIT_CARD]" in filtered

    def test_custom_pattern_filtering(self):
        """Test custom regex pattern filtering."""
        filter = LogFilter(
            custom_patterns=[
                (r"SECRET_\w+", "[REDACTED_SECRET]")
            ]
        )

        log_message = "Configuration: SECRET_DATABASE_PASSWORD=abc123"
        filtered = filter.filter(log_message)

        assert "SECRET_DATABASE_PASSWORD" not in filtered
        assert "[REDACTED_SECRET]" in filtered

    def test_filter_chaining(self):
        """Test multiple filters applied in sequence."""
        filter = LogFilter()

        log_message = (
            "User john@example.com logged in with password='secret' "
            "using API key sk_test_123"
        )
        filtered = filter.filter(log_message)

        # All should be redacted
        assert "john@example.com" not in filtered
        assert "secret" not in filtered
        assert "sk_test_123" not in filtered

    def test_performance_optimization(self):
        """Test filter performance with large logs."""
        filter = LogFilter()

        # Large log message
        log_message = "Normal log data " * 10000

        start = time.time()
        filtered = filter.filter(log_message)
        duration = time.time() - start

        # Should complete quickly (< 0.1s)
        assert duration < 0.1

    # Cover all 19 untested statements
```

#### D. SSRF Protection (Priority 1 - Security Critical)

**ssrf_protection.py** (39 untested statements):
```python
# tests/unit/test_ssrf_protection.py (create new)
class TestSSRFProtection:
    """SSRF protection mechanism tests."""

    def test_private_ipv4_detection(self):
        """Test detection of private IPv4 addresses."""
        ssrf = SSRFProtection()

        # Should block private IP ranges
        with pytest.raises(SSRFProtectionError, match="private"):
            ssrf.validate_url("http://192.168.1.1/api")

        with pytest.raises(SSRFProtectionError):
            ssrf.validate_url("http://10.0.0.1/api")

        with pytest.raises(SSRFProtectionError):
            ssrf.validate_url("http://172.16.0.1/api")

    def test_localhost_detection(self):
        """Test localhost detection."""
        ssrf = SSRFProtection()

        # All localhost variants should be blocked
        with pytest.raises(SSRFProtectionError, match="localhost"):
            ssrf.validate_url("http://localhost/api")

        with pytest.raises(SSRFProtectionError):
            ssrf.validate_url("http://127.0.0.1/api")

        with pytest.raises(SSRFProtectionError):
            ssrf.validate_url("http://127.0.0.2/api")  # 127.0.0.0/8

    def test_ipv6_private_address_detection(self):
        """Test IPv6 private address detection."""
        ssrf = SSRFProtection()

        # IPv6 localhost
        with pytest.raises(SSRFProtectionError):
            ssrf.validate_url("http://[::1]/api")

        # IPv6 link-local
        with pytest.raises(SSRFProtectionError):
            ssrf.validate_url("http://[fe80::1]/api")

    def test_dns_rebinding_protection(self):
        """Test DNS rebinding attack protection."""
        ssrf = SSRFProtection(check_dns_rebinding=True)

        # Mock DNS resolution to return private IP
        def mock_resolve(hostname):
            return ["192.168.1.1"]

        with patch('socket.gethostbyname_ex', return_value=(None, None, mock_resolve("evil.com"))):
            with pytest.raises(SSRFProtectionError, match="DNS rebinding"):
                ssrf.validate_url("http://evil.com/api")

    def test_url_parsing_validation(self):
        """Test URL parsing and structure validation."""
        ssrf = SSRFProtection()

        # Malformed URLs
        with pytest.raises(SSRFProtectionError, match="Invalid URL"):
            ssrf.validate_url("not_a_url")

        with pytest.raises(SSRFProtectionError):
            ssrf.validate_url("http://")

        with pytest.raises(SSRFProtectionError):
            ssrf.validate_url("://example.com")

    def test_protocol_validation(self):
        """Test protocol restriction (http/https only)."""
        ssrf = SSRFProtection(allowed_protocols=["http", "https"])

        # Should block non-HTTP protocols
        with pytest.raises(SSRFProtectionError, match="protocol"):
            ssrf.validate_url("ftp://example.com/file")

        with pytest.raises(SSRFProtectionError):
            ssrf.validate_url("file:///etc/passwd")

        with pytest.raises(SSRFProtectionError):
            ssrf.validate_url("gopher://example.com")

        # Should allow HTTP/HTTPS
        ssrf.validate_url("http://example.com")
        ssrf.validate_url("https://example.com")

    def test_port_blacklisting(self):
        """Test port blacklist enforcement."""
        ssrf = SSRFProtection(
            blocked_ports=[22, 23, 3306, 5432, 6379]  # SSH, Telnet, MySQL, PostgreSQL, Redis
        )

        # Should block internal service ports
        with pytest.raises(SSRFProtectionError, match="port"):
            ssrf.validate_url("http://example.com:22")

        with pytest.raises(SSRFProtectionError):
            ssrf.validate_url("http://example.com:3306")

        # Should allow common web ports
        ssrf.validate_url("http://example.com:80")
        ssrf.validate_url("http://example.com:443")

    def test_hostname_blacklisting(self):
        """Test hostname blacklist."""
        ssrf = SSRFProtection(
            blocked_hostnames=["metadata.google.internal", "169.254.169.254"]
        )

        # Should block cloud metadata endpoints
        with pytest.raises(SSRFProtectionError, match="hostname"):
            ssrf.validate_url("http://metadata.google.internal/")

        with pytest.raises(SSRFProtectionError):
            ssrf.validate_url("http://169.254.169.254/latest/meta-data")

    def test_valid_public_urls(self):
        """Test that valid public URLs are allowed."""
        ssrf = SSRFProtection()

        # Should allow legitimate public URLs
        ssrf.validate_url("https://api.example.com/data")
        ssrf.validate_url("http://cdn.example.org/assets")
        ssrf.validate_url("https://github.com/user/repo")

    def test_exception_handling(self):
        """Test proper exception handling and messages."""
        ssrf = SSRFProtection()

        try:
            ssrf.validate_url("http://192.168.1.1")
        except SSRFProtectionError as e:
            assert "private IP" in str(e).lower()
            assert e.url == "http://192.168.1.1"

    # Cover all 39 untested statements
```

### 2. Test Organization

```
tests/
├── unit/
│   ├── test_security.py                   ✓ enhance (existing tests)
│   ├── test_circuit_breaker.py            + create (46 statements)
│   ├── test_dos_protection.py             + create (18 statements)
│   ├── test_log_filter.py                 + create (19 statements)
│   └── test_ssrf_protection.py            + create (39 statements)
└── integration/
    ├── test_config_security.py            ✓ keep
    └── test_security_integration.py       + create (integration tests)
```

## Implementation Steps

1. **Phase 1: SSRF Protection** (3-4 hours)
   - Create tests/unit/test_ssrf_protection.py (39 statements)
   - **CRITICAL**: Protects against Server-Side Request Forgery
   - Test all private IP ranges, DNS rebinding, protocol validation

2. **Phase 2: Circuit Breaker** (3-4 hours)
   - Create tests/unit/test_circuit_breaker.py (46 statements)
   - **HIGH PRIORITY**: Prevents cascading failures
   - Test state transitions, concurrent access, metrics

3. **Phase 3: DoS Protection** (2-3 hours)
   - Create tests/unit/test_dos_protection.py (18 statements)
   - **CRITICAL**: Prevents denial of service
   - Test connection limiting, throttling, resource protection

4. **Phase 4: Log Filter** (2-3 hours)
   - Create tests/unit/test_log_filter.py (19 statements)
   - **CRITICAL**: Prevents secret/PII leakage
   - Test secret detection, PII redaction, custom patterns

5. **Phase 5: Integration Testing** (1-2 hours)
   - Create tests/integration/test_security_integration.py
   - Test security modules working together
   - End-to-end security scenarios

6. **Phase 6: Documentation** (1 hour)
   - Document security test patterns
   - Update security documentation
   - CI configuration for security tests

## Testing Strategy

### Security Testing Principles
- **Attack Scenarios**: Test actual attack patterns
- **Defense in Depth**: Test multiple security layers
- **Fail Secure**: Verify failures block access
- **No False Negatives**: Security must not miss threats

### Unit Tests
- Test each security mechanism in isolation
- Test both positive cases (allowed) and negative cases (blocked)
- Test edge cases and boundary conditions
- Test concurrent access and race conditions

### Integration Tests
- Test security modules working together
- Test real attack scenarios
- Verify defense-in-depth

### Performance Tests
- Security checks should not significantly impact performance
- Test under load

## Acceptance Criteria

- [ ] **circuit_breaker.py** coverage: 27.06% → 95%+
- [ ] **dos_protection.py** coverage: 16.13% → 95%+
- [ ] **log_filter.py** coverage: 24.39% → 95%+
- [ ] **ssrf_protection.py** coverage: 21.43% → 95%+
- [ ] All security tests pass on all platforms
- [ ] All tests pass with Python 3.12-3.15-dev
- [ ] No test flakiness
- [ ] Overall security module coverage: **25% → 95%+**
- [ ] diff-cover shows 100% coverage on new tests
- [ ] All attack scenarios tested
- [ ] All edge cases covered
- [ ] Concurrent access tested
- [ ] Performance verified (< 10ms overhead per check)
- [ ] Documentation updated with security testing patterns

## Related Files

### Source Files:
- `src/nhl_scrabble/security/circuit_breaker.py` - Circuit breaker (69 statements, 46 untested)
- `src/nhl_scrabble/security/dos_protection.py` - DoS protection (23 statements, 18 untested)
- `src/nhl_scrabble/security/log_filter.py` - Log filtering (29 statements, 19 untested)
- `src/nhl_scrabble/security/ssrf_protection.py` - SSRF protection (54 statements, 39 untested)
- `src/nhl_scrabble/exceptions.py` - Security exceptions (SSRFProtectionError, SecurityError, CircuitBreakerOpenError)

### Test Files:
- `tests/unit/test_security.py` - Enhance existing tests
- `tests/integration/test_config_security.py` - Keep integration tests
- `tests/unit/test_circuit_breaker.py` - Create (46 statements)
- `tests/unit/test_dos_protection.py` - Create (18 statements)
- `tests/unit/test_log_filter.py` - Create (19 statements)
- `tests/unit/test_ssrf_protection.py` - Create (39 statements)
- `tests/integration/test_security_integration.py` - Create

## Dependencies

- **Independent**: Can be implemented immediately
- **HIGH PRIORITY**: Security is critical - should be prioritized
- **Complements other test coverage tasks** but more urgent due to security implications

## Additional Notes

### Why HIGH Priority

1. **Security Critical**: These modules protect against real attacks (SSRF, DoS)
2. **Low Coverage = High Risk**: 25% coverage means 75% of security code is untested
3. **Compliance**: Security testing may be required for compliance/audits
4. **Data Protection**: Log filters prevent secret/PII leakage
5. **Stability**: Circuit breaker prevents cascading failures

### Security Testing Best Practices

- **Think Like an Attacker**: Test malicious inputs
- **No Shortcuts**: Security must be bulletproof
- **Fail Secure**: Default to deny/block when in doubt
- **Defense in Depth**: Test multiple layers
- **Document Attack Vectors**: Help future developers

### Attack Scenarios to Test

**SSRF Attacks:**
- Private IP access (192.168.x.x, 10.x.x.x, 127.0.0.1)
- Cloud metadata endpoints (169.254.169.254)
- DNS rebinding
- Protocol smuggling (file://, gopher://, ftp://)
- Port scanning via SSRF

**DoS Attacks:**
- Connection exhaustion
- Slowloris (slow requests)
- Resource exhaustion
- Amplification attacks

**Secret Leakage:**
- API keys in logs
- Passwords in error messages
- Tokens in debug output
- PII in analytics

### Performance Considerations

Security checks add overhead:
- SSRF validation: < 5ms per URL
- Circuit breaker: < 1ms per request
- DoS protection: < 2ms per connection
- Log filtering: < 10ms per log entry

All should be tested under load.

### Platform Compatibility

Security tests must pass on:
- Linux (primary)
- macOS (DNS/network behavior may differ)
- Windows (path handling, networking)

## Implementation Notes

*To be filled during implementation:*
- Attack scenarios discovered
- Security edge cases found
- Performance impact measured
- Actual effort vs estimated
- Coverage improvements achieved
- Security vulnerabilities found and fixed
