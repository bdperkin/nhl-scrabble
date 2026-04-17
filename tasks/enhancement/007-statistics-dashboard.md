# Add Interactive Statistics Dashboard

**GitHub Issue**: #147 - https://github.com/bdperkin/nhl-scrabble/issues/147

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

6-8 hours

## Description

Create an interactive terminal dashboard showing live statistics with charts and visualizations using Rich library.

Currently static text output. Users cannot see visual representations of data.

## Proposed Solution

```python
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout

class StatisticsDashboard:
    def run(self):
        layout = Layout()
        layout.split_row(
            Layout(name="teams"),
            Layout(name="players"),
        )

        with Live(layout, refresh_per_second=1):
            # Update dashboard
            pass
```

```bash
# Launch dashboard
nhl-scrabble dashboard

# Dashboard with filters
nhl-scrabble dashboard --division Atlantic
```

## Implementation Steps

1. Design dashboard layout
1. Implement Rich visualizations
1. Add live updates
1. Add keyboard controls
1. Add tests
1. Update documentation

## Acceptance Criteria

- [ ] Interactive dashboard implemented
- [ ] Charts and tables displayed
- [ ] Keyboard navigation works
- [ ] Live updates supported
- [ ] Tests pass
- [ ] Documentation updated

## Related Files

- `src/nhl_scrabble/dashboard.py` - New module
- `src/nhl_scrabble/cli.py` - Add dashboard command

## Dependencies

- Rich (already installed)

## Additional Notes

**Benefits**: Visual data exploration, better UX, impressive demo

## Implementation Notes

*To be filled during implementation*
