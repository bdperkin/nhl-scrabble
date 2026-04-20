# Web Interface Test Coverage (30% → 85%)

**GitHub Issue**: #254 - https://github.com/bdperkin/nhl-scrabble/issues/254

**Parent Task**: #221 - Comprehensive Test Coverage (sub-task 2 of 8)

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

3-4 hours

## Description

Improve test coverage for web interface modules (`src/nhl_scrabble/web/`) from ~30% to 85%+ by adding tests for route handlers, template rendering, form validation, API endpoints, and error handling.

**Parent Task**: tasks/testing/002-comprehensive-test-coverage-90-100.md (Phase 3)

## Proposed Solution

```python
# tests/integration/test_web_interface.py
import pytest
from nhl_scrabble.web.app import app

class TestWebInterface:
    @pytest.fixture
    def client(self):
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_homepage_loads(self, client):
        response = client.get('/')
        assert response.status_code == 200
        assert b"NHL Scrabble" in response.data

    def test_api_teams_endpoint(self, client):
        response = client.get('/api/teams')
        assert response.status_code == 200
        data = response.get_json()
        assert 'teams' in data

    def test_404_error_handling(self, client):
        response = client.get('/nonexistent')
        assert response.status_code == 404
```

## Acceptance Criteria

- [ ] Web coverage improved from 30% to 85%+
- [ ] All routes tested
- [ ] API endpoints tested
- [ ] Error handlers tested
- [ ] Template rendering tested

## Dependencies

- **Parent**: #221

## Implementation Notes

*To be filled during implementation*
