# Add Docker Support

**GitHub Issue**: #157 - https://github.com/bdperkin/nhl-scrabble/issues/157

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

4-6 hours

## Description

Add Docker support for containerized deployment and easy distribution.

## Proposed Solution

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -e .
CMD ["nhl-scrabble", "analyze"]
```

```bash
# Build image
docker build -t nhl-scrabble .

# Run analysis
docker run nhl-scrabble

# Run API server
docker run -p 8000:8000 nhl-scrabble serve
```

## Acceptance Criteria

- [ ] Dockerfile created
- [ ] Docker Compose config added
- [ ] Image builds successfully
- [ ] Container runs analysis
- [ ] Documentation updated

## Related Files

- `Dockerfile`
- `docker-compose.yml`
- `.dockerignore`

## Dependencies

None

## Implementation Notes

*To be filled during implementation*
