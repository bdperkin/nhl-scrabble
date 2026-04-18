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

- [x] SSL verification explicitly enabled in all requests
- [x] Cannot disable SSL verification via config
- [x] SSL errors properly caught and logged
- [x] Uses certifi CA bundle
- [x] Tests verify SSL enforcement
- [x] Documentation updated
- [x] No `verify=False` in codebase

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

**Implemented**: 2026-04-18
**Branch**: security/006-ssl-verification
**Status**: Implementation complete, ready for PR

### Actual Implementation

Followed the proposed solution closely with all planned features:

1. **SSL Verification Enforcement**:

   - Added `verify_ssl` parameter to `NHLApiClient.__init__()` (default: True)
   - Raises `ValueError` if `verify_ssl=False` is attempted
   - Prevents accidental SSL verification bypass

1. **Certifi CA Bundle**:

   - Added `import certifi` to nhl_client.py
   - Set `self.ca_bundle = certifi.where()` in constructor
   - All requests use `verify=self.ca_bundle` parameter
   - Logged CA bundle path during initialization

1. **Explicit SSL Verification**:

   - Updated both `get_teams()` and `get_team_roster()` methods
   - Added explicit `verify=self.ca_bundle` to all `session.get()` calls
   - SSL verification cannot be bypassed

1. **SSL Error Handling**:

   - Added new `NHLApiSSLError` exception class
   - Exported in `api/__init__.py` module
   - SSL errors caught and logged with descriptive messages
   - SSL errors are NOT retried (permanent security failure)
   - Added to get_teams() and get_team_roster() methods

1. **Bug Fixes**:

   - Fixed initialization order: `_closed = False` set before potential exceptions
   - Added `hasattr(self, "session")` check in `close()` method
   - Prevents AttributeError if constructor fails before session creation

### Testing

Created comprehensive test suite in `tests/unit/test_ssl_verification.py`:

- **10 unit tests** covering all aspects of SSL verification
- 4 tests for SSL verification enforcement
- 2 tests for SSL verification in requests
- 4 tests for SSL error handling
- All tests passing (10/10)
- Code coverage: 84.58% on nhl_client.py (improvement from baseline)

### Code Quality

- ✅ Ruff linting: All checks passed
- ✅ MyPy type checking: Success, no issues
- ✅ All 325 existing tests: Passing
- ✅ Pre-commit hooks: Ready (imports auto-sorted)

### Documentation Updates

- Updated `NHLApiClient` class docstring with SSL/TLS security notes
- Updated `__init__()` docstring with verify_ssl parameter
- Added CHANGELOG.md entry in "Security" section
- Documented SSL error handling in exception docstrings

### Actual vs Estimated Effort

- **Estimated**: 1-2h
- **Actual**: ~1.5h
- **On target**: Implementation complexity matched estimate

### Deviations from Plan

1. **No certificate pinning**:

   - Decided against implementing certificate pinning
   - NHL API certificate may rotate without notice
   - Trust CA bundle is more maintainable
   - Matches best practices from task description

1. **ValueError instead of SecurityError**:

   - Used built-in `ValueError` for verify_ssl=False
   - More Pythonic than custom exception
   - Clear semantic meaning for invalid parameter

1. **Session attribute check**:

   - Added `hasattr(self, "session")` in close() method
   - Prevents issues if initialization fails
   - Not in original plan but necessary for robustness

### Security Benefits

- ✅ Prevents man-in-the-middle (MITM) attacks
- ✅ Ensures connection authenticity via trusted CAs
- ✅ Protects API data integrity
- ✅ Cannot be accidentally disabled
- ✅ Uses up-to-date CA bundle via certifi
- ✅ SSL errors logged for security monitoring

### Related PRs

- PR pending: Will create after commit

### Lessons Learned

1. **Initialization order matters**: Set state variables before raising exceptions
1. **Test session type**: Use `patch.object(client.session)` for cached sessions
1. **Import sorting**: Ruff auto-fix is helpful for I001 violations
1. **Error granularity**: Specific SSL error logging helps debugging
1. **No retries for security**: SSL errors should fail fast, not retry
