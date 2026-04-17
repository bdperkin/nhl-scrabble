# Enforce SSL/TLS Certificate Verification

**GitHub Issue**: #135 - https://github.com/bdperkin/nhl-scrabble/issues/135

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

1-2 hours

## Description

Enforce strict SSL/TLS certificate verification for all NHL API requests to prevent man-in-the-middle (MITM) attacks.

Currently, SSL verification is enabled by default in requests, but not explicitly enforced. This creates risks if:

- Code is modified to disable verification (`verify=False`)
- Certificate validation is bypassed for debugging
- Custom SSL contexts are used incorrectly

Need to:

- Explicitly enforce `verify=True` in all requests
- Prevent accidental verification bypass
- Add certificate pinning for NHL API
- Log SSL verification failures
- Test certificate validation

## Current State

```python
# src/nhl_scrabble/api/nhl_client.py
class NHLApiClient:
    def get_team_roster(self, team_abbrev: str):
        url = f"https://api-web.nhle.com/v1/roster/{team_abbrev}/current"
        # verify=True is default, but not explicit
        response = self.session.get(url, timeout=self.timeout)
```

**Risks**:

- Developer could add `verify=False` for debugging
- No certificate pinning (trusts any valid CA)
- No explicit SSL enforcement policy
- No SSL error logging

## Proposed Solution

### 1. Explicit SSL Enforcement

```python
class NHLApiClient:
    def __init__(self, verify_ssl: bool = True):
        if not verify_ssl:
            raise SecurityError("SSL verification cannot be disabled")

        self.verify_ssl = verify_ssl
        self.session = requests.Session()

    def get_team_roster(self, team_abbrev: str):
        # Explicitly require SSL verification
        response = self.session.get(
            url,
            timeout=self.timeout,
            verify=True,  # Explicit!
        )
```

### 2. Certificate Pinning (Optional)

```python
import ssl
import certifi

class NHLApiClient:
    def __init__(self):
        # Use certifi CA bundle
        self.ca_bundle = certifi.where()

        # Optional: Pin NHL API certificate
        self.expected_cert_fingerprint = (
            "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
        )

    def get_team_roster(self, team_abbrev: str):
        response = self.session.get(
            url,
            verify=self.ca_bundle,  # Use certifi CAs
        )

        # Verify certificate pinning
        self._verify_certificate_pin(response)
```

### 3. SSL Error Handling

```python
import requests.exceptions

class NHLApiClient:
    def get_team_roster(self, team_abbrev: str):
        try:
            response = self.session.get(url, verify=True)
        except requests.exceptions.SSLError as e:
            logger.error(f"SSL verification failed: {e}")
            raise SecurityError(
                f"SSL certificate verification failed for {url}"
            ) from e
```

## Implementation Steps

1. Add explicit `verify=True` to all requests calls
1. Prevent `verify=False` in constructor
1. Use certifi CA bundle for verification
1. Add SSL error handling and logging
1. Add configuration option for CA bundle path
1. Add tests for SSL verification
1. Document SSL requirements

## Testing Strategy

**Unit Tests**:

```python
def test_ssl_verification_enforced():
    client = NHLApiClient()

    # Should use SSL verification
    with patch("requests.Session.get") as mock_get:
        client.get_team_roster("TOR")

        call_args = mock_get.call_args
        assert call_args.kwargs["verify"] is True

def test_ssl_verification_cannot_be_disabled():
    with pytest.raises(SecurityError):
        NHLApiClient(verify_ssl=False)
```

**Integration Tests**:

```bash
# Test against live NHL API
pytest tests/integration/test_ssl_verification.py
```

## Acceptance Criteria

- [ ] SSL verification explicitly enabled in all requests
- [ ] Cannot disable SSL verification via config
- [ ] SSL errors properly caught and logged
- [ ] Uses certifi CA bundle
- [ ] Tests verify SSL enforcement
- [ ] Documentation updated
- [ ] No `verify=False` in codebase

## Related Files

- `src/nhl_scrabble/api/nhl_client.py` - Enforce SSL verification
- `src/nhl_scrabble/config.py` - SSL configuration options
- `tests/unit/test_ssl_verification.py` - New tests

## Dependencies

- `certifi` - Already installed, provides CA bundle
- No blocking dependencies

## Additional Notes

**Security Benefits**:

- Prevents MITM attacks
- Ensures connection authenticity
- Protects API credentials

**Certificate Pinning Considerations**:

- More secure but brittle (breaks when cert rotates)
- NHL API certificate may change without notice
- Recommended: Trust CA, don't pin specific cert

**Best Practices**:

- Always use `verify=True` (never disable)
- Use certifi for up-to-date CA bundle
- Log SSL errors for monitoring
- Document SSL requirements

## Implementation Notes

*To be filled during implementation*
