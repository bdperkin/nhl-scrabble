# Expand Test Coverage of Interactive Modules

**GitHub Issue**: #591 - https://github.com/bdperkin/nhl-scrabble/issues/591

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

16-20 hours

## Description

**Interactive/shell modules have zero test coverage despite having test files**, leaving the entire interactive REPL functionality untested. Current coverage is **0.00%**, with **~407 untested statements**:

- **interactive/shell.py**: 0.00% (405 statements untested)
- **interactive/__init__.py**: 0.00% (2 statements untested)

**Total missing coverage**: ~407 statements across 2 files

**Similar to Task 036**: Test files **already exist** but have **0% coverage**, indicating tests are incomplete, not running properly, or not configured correctly.

This represents critical gaps in quality assurance for:
- Interactive shell/REPL functionality
- Command parsing and execution
- User input handling and validation
- Terminal UI/TUI components
- Shell session management
- Interactive help system
- Command history
- Auto-completion
- Error handling in interactive mode

## Current State

### Existing Tests (But 0% Coverage):

**tests/unit/test_interactive_shell.py** - EXISTS but 0% coverage
- Test file exists but shell.py has 0% coverage (405 statements)
- Suggests tests are incomplete or not executing source code

**tests/integration/test_cli_interactive.py** - Integration tests
- EXISTS but also reports 0% coverage
- May test CLI integration but not shell internals

### Coverage Breakdown:

**interactive/shell.py (405 statements, 0% coverage):**
```
Lines missing: 3-700 (entire file)
Features untested:
- Interactive shell initialization
- Command parsing and routing
- REPL loop execution
- User input handling
- Command validation
- Shell commands (help, exit, clear, etc.)
- Session state management
- Command history tracking
- Auto-completion logic
- Error handling and display
- Terminal formatting
- Prompt customization
- Multi-line input handling
- Shell configuration
- Interactive help system
```

## Proposed Solution

### Phase 0: Investigation (1-2 hours)
**Critical First Step** - Understand why existing tests have 0% coverage:
1. Review test_interactive_shell.py and test_cli_interactive.py
2. Identify incomplete tests or configuration issues
3. Check if tests are running in CI
4. Document findings

### 1. Comprehensive Interactive Shell Testing

**interactive/shell.py** (405 statements):

```python
# tests/unit/test_interactive_shell.py (enhance existing)
class TestInteractiveShell:
    """Comprehensive interactive shell tests."""

    @pytest.fixture
    def shell(self):
        """Create shell instance for testing."""
        return InteractiveShell()

    def test_shell_initialization(self, shell):
        """Test shell initializes with correct defaults."""
        assert shell is not None
        assert shell.prompt == "nhl-scrabble> "
        assert shell.running is False

    def test_command_parsing_simple(self, shell):
        """Test simple command parsing."""
        cmd, args = shell.parse_command("help")
        assert cmd == "help"
        assert args == []

    def test_command_parsing_with_args(self, shell):
        """Test command parsing with arguments."""
        cmd, args = shell.parse_command("analyze --team WSH")
        assert cmd == "analyze"
        assert "--team" in args
        assert "WSH" in args

    def test_command_parsing_quoted_args(self, shell):
        """Test parsing arguments with quotes."""
        cmd, args = shell.parse_command('search "Alex Ovechkin"')
        assert cmd == "search"
        assert "Alex Ovechkin" in args

    def test_command_routing(self, shell, monkeypatch):
        """Test command routing to handlers."""
        called = []

        def mock_help_handler(args):
            called.append("help")

        monkeypatch.setattr(shell, "cmd_help", mock_help_handler)
        shell.execute_command("help")

        assert "help" in called

    def test_repl_loop_execution(self, shell, monkeypatch):
        """Test REPL loop execution."""
        inputs = iter(["help", "exit"])

        def mock_input(prompt):
            return next(inputs)

        monkeypatch.setattr("builtins.input", mock_input)

        shell.run()
        # Verify loop executed and exited cleanly

    def test_user_input_handling(self, shell, monkeypatch):
        """Test user input validation and sanitization."""
        # Test empty input
        result = shell.handle_input("")
        assert result is None  # Should ignore empty input

        # Test whitespace-only input
        result = shell.handle_input("   ")
        assert result is None

    def test_command_validation(self, shell):
        """Test command validation."""
        # Valid command
        assert shell.is_valid_command("help") is True
        assert shell.is_valid_command("exit") is True

        # Invalid command
        assert shell.is_valid_command("invalid_cmd") is False

    def test_help_command(self, shell, capsys):
        """Test help command displays available commands."""
        shell.cmd_help([])
        captured = capsys.readouterr()
        assert "Available commands:" in captured.out
        assert "help" in captured.out
        assert "exit" in captured.out

    def test_exit_command(self, shell):
        """Test exit command stops the shell."""
        shell.running = True
        shell.cmd_exit([])
        assert shell.running is False

    def test_clear_command(self, shell, monkeypatch):
        """Test clear command clears terminal."""
        cleared = []

        def mock_clear():
            cleared.append(True)

        monkeypatch.setattr("os.system", lambda x: cleared.append(True))
        shell.cmd_clear([])

        assert len(cleared) > 0

    def test_session_state_management(self, shell):
        """Test session state tracking."""
        shell.start_session()
        assert shell.session_id is not None
        assert shell.session_start_time is not None

        shell.end_session()
        assert shell.session_end_time is not None

    def test_command_history_tracking(self, shell):
        """Test command history is recorded."""
        shell.execute_command("help")
        shell.execute_command("exit")

        history = shell.get_history()
        assert len(history) == 2
        assert "help" in history
        assert "exit" in history

    def test_command_history_navigation(self, shell):
        """Test navigating command history with up/down arrows."""
        shell.add_to_history("command1")
        shell.add_to_history("command2")
        shell.add_to_history("command3")

        # Navigate up
        assert shell.history_previous() == "command3"
        assert shell.history_previous() == "command2"
        assert shell.history_previous() == "command1"

        # Navigate down
        assert shell.history_next() == "command2"

    def test_auto_completion(self, shell):
        """Test command auto-completion."""
        completions = shell.get_completions("he")
        assert "help" in completions

        completions = shell.get_completions("ex")
        assert "exit" in completions

    def test_auto_completion_no_matches(self, shell):
        """Test auto-completion with no matches."""
        completions = shell.get_completions("xyz")
        assert len(completions) == 0

    def test_error_handling_invalid_command(self, shell, capsys):
        """Test error handling for invalid commands."""
        shell.execute_command("invalid_command")
        captured = capsys.readouterr()
        assert "Unknown command" in captured.out or "not found" in captured.out

    def test_error_handling_command_exception(self, shell, capsys, monkeypatch):
        """Test error handling when command raises exception."""
        def failing_command(args):
            raise ValueError("Command failed")

        monkeypatch.setattr(shell, "cmd_test", failing_command)
        shell.execute_command("test")

        captured = capsys.readouterr()
        assert "Error" in captured.out or "failed" in captured.out

    def test_terminal_formatting(self, shell):
        """Test terminal text formatting."""
        # Bold
        formatted = shell.format_bold("text")
        assert "\033[1m" in formatted or "<b>" in formatted

        # Color
        formatted = shell.format_color("text", "red")
        assert "\033[" in formatted or "red" in formatted

    def test_prompt_customization(self, shell):
        """Test custom prompt configuration."""
        shell.set_prompt("custom> ")
        assert shell.prompt == "custom> "

    def test_multi_line_input_handling(self, shell, monkeypatch):
        """Test handling multi-line input (e.g., for long commands)."""
        inputs = iter(["analyze \\", "--team WSH", ""])

        def mock_input(prompt):
            return next(inputs)

        monkeypatch.setattr("builtins.input", mock_input)

        full_command = shell.read_multi_line_input()
        assert "analyze" in full_command
        assert "WSH" in full_command

    def test_shell_configuration(self, shell):
        """Test shell configuration options."""
        config = {
            "prompt": ">>> ",
            "history_size": 100,
            "auto_complete": True
        }
        shell.configure(config)

        assert shell.prompt == ">>> "
        assert shell.history_size == 100
        assert shell.auto_complete is True

    def test_interactive_help_system(self, shell, capsys):
        """Test interactive help for specific commands."""
        shell.cmd_help(["analyze"])
        captured = capsys.readouterr()
        assert "analyze" in captured.out
        # Should show command-specific help

    def test_keyboard_interrupt_handling(self, shell, monkeypatch):
        """Test handling Ctrl+C (KeyboardInterrupt)."""
        def raise_interrupt(prompt):
            raise KeyboardInterrupt()

        monkeypatch.setattr("builtins.input", raise_interrupt)

        # Should handle gracefully without crashing
        shell.run()
        # Verify shell handled interrupt

    def test_eof_handling(self, shell, monkeypatch):
        """Test handling Ctrl+D (EOFError)."""
        def raise_eof(prompt):
            raise EOFError()

        monkeypatch.setattr("builtins.input", raise_eof)

        # Should exit gracefully
        shell.run()
        assert shell.running is False

    # Cover all 405 statements
```

### 2. Integration Testing

```python
# tests/integration/test_cli_interactive.py (enhance existing)
class TestInteractiveCLIIntegration:
    """Integration tests for interactive CLI."""

    def test_launch_interactive_mode(self):
        """Test launching interactive mode from CLI."""
        # Test `nhl-scrabble interactive` command
        pass

    def test_execute_commands_in_session(self):
        """Test executing multiple commands in one session."""
        pass

    def test_session_persistence(self):
        """Test session state persists across commands."""
        pass

    def test_exit_from_interactive_mode(self):
        """Test cleanly exiting interactive mode."""
        pass
```

### 3. Test Organization

```
tests/
├── unit/
│   └── test_interactive_shell.py       ✓ enhance (405 statements)
└── integration/
    └── test_cli_interactive.py         ✓ enhance
```

## Implementation Steps

1. **Phase 0: Investigation** (1-2 hours)
   - Review existing test files
   - Understand why coverage is 0%
   - Document findings

2. **Phase 1: Core Shell Functionality** (6-8 hours)
   - Test shell initialization and configuration
   - Test command parsing and routing
   - Test REPL loop execution
   - Test user input handling

3. **Phase 2: Interactive Features** (4-6 hours)
   - Test command history
   - Test auto-completion
   - Test multi-line input
   - Test help system

4. **Phase 3: Error Handling** (2-3 hours)
   - Test invalid command handling
   - Test exception handling
   - Test keyboard interrupts (Ctrl+C, Ctrl+D)

5. **Phase 4: Integration Testing** (2-3 hours)
   - Test CLI integration
   - Test session management
   - Test end-to-end workflows

6. **Phase 5: Documentation** (1 hour)
   - Update test documentation
   - CI configuration

## Testing Strategy

### Unit Tests
- Test shell components in isolation
- Mock user input with monkeypatch
- Test command handlers individually
- Test utility functions

### Integration Tests
- Test interactive mode end-to-end
- Test with real user input simulation
- Test session workflows

### Special Considerations
- **Interactive testing is challenging**: Requires mocking input/output
- **Terminal-dependent features**: May need platform-specific handling
- **Signal handling**: Test Ctrl+C, Ctrl+D gracefully

## Acceptance Criteria

- [ ] Investigation complete - understand why tests had 0% coverage
- [ ] **interactive/shell.py** coverage: 0% → 95%+
- [ ] All shell commands tested
- [ ] Command parsing and routing tested
- [ ] User input handling tested
- [ ] Error handling tested (invalid commands, exceptions, interrupts)
- [ ] Command history tested
- [ ] Auto-completion tested
- [ ] All tests pass on all platforms
- [ ] All tests pass with Python 3.12-3.15-dev
- [ ] No test flakiness
- [ ] diff-cover shows 100% coverage
- [ ] Documentation updated

## Related Files

### Source Files:
- `src/nhl_scrabble/interactive/shell.py` - Interactive shell (405 statements)
- `src/nhl_scrabble/interactive/__init__.py` - Module exports (2 statements)

### Test Files:
- `tests/unit/test_interactive_shell.py` - Enhance existing (405 statements)
- `tests/integration/test_cli_interactive.py` - Enhance existing
- `tests/conftest.py` - Add interactive testing fixtures

## Dependencies

- **Independent**: Can be implemented immediately
- **Complements Tasks 033-037**: Part of comprehensive test coverage initiative
- **Investigation Required**: Similar to Task 036 (tests exist but 0% coverage)

## Additional Notes

### Why This Task

1. **User-Facing**: Interactive mode is a key user interface
2. **Complex**: REPL/shell functionality is challenging to test
3. **0% Coverage Risk**: Entire interactive functionality is untested
4. **Tests Exist**: Similar to Task 036 - investigation needed

### Interactive Testing Challenges

**Mocking User Input**:
- Use `monkeypatch.setattr("builtins.input", mock_fn)`
- Simulate keyboard input sequences
- Test multi-line input

**Terminal Dependencies**:
- Some features may be terminal-specific
- May need platform-specific handling
- Test with/without TTY

**Signal Handling**:
- Test KeyboardInterrupt (Ctrl+C)
- Test EOFError (Ctrl+D)
- Verify graceful shutdown

### Testing Patterns

```python
# Mock user input pattern
@pytest.fixture
def mock_user_input(monkeypatch):
    def _mock_input(commands):
        inputs = iter(commands)
        monkeypatch.setattr(
            "builtins.input",
            lambda prompt: next(inputs)
        )
    return _mock_input

def test_command_sequence(shell, mock_user_input):
    mock_user_input(["help", "analyze", "exit"])
    shell.run()
    # Verify commands executed
```

### Platform Compatibility

All tests must pass on:
- Linux (primary)
- macOS (terminal behavior may differ)
- Windows (different terminal handling)

## Implementation Notes

*To be filled during implementation:*
- Investigation findings (why 0% coverage)
- Interactive testing patterns discovered
- Terminal compatibility challenges
- Actual effort vs estimated
- Coverage improvements achieved

---

## Summary

This task completes the **6-task comprehensive test coverage initiative** covering the entire NHL Scrabble application:

**Tasks 033-038 Combined**:
- ~2,905 untested statements
- 106-144 hours total effort
- Coverage target: 90.21% → 97%+
- Complete application coverage
