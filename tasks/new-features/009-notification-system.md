# Add Notification System

**GitHub Issue**: #152 - https://github.com/bdperkin/nhl-scrabble/issues/152

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

6-8 hours

## Description

Add notification system for roster changes, score updates, and milestones via email, Slack, or webhooks.

## Proposed Solution

```bash
# Configure notifications
nhl-scrabble notify config --email user@example.com
nhl-scrabble notify config --slack-webhook https://hooks.slack.com/...

# Watch with notifications
nhl-scrabble watch --notify-on-change
```

## Acceptance Criteria

- [ ] Email notifications working
- [ ] Slack notifications working
- [ ] Webhook notifications working
- [ ] Tests pass

## Related Files

- `src/nhl_scrabble/notifications.py`

## Dependencies

- `smtplib` (stdlib)
- `requests` (existing)

## Implementation Notes

*To be filled during implementation*
