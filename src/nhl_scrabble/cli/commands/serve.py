"""Serve command for NHL Scrabble CLI."""

from __future__ import annotations

from pathlib import Path

import click

from nhl_scrabble.config import Config
from nhl_scrabble.i18n import _
from nhl_scrabble.logging_config import setup_logging


@click.command()
@click.option(
    "--host",
    default="127.0.0.1",
    help=_("Host address to bind server (default: 127.0.0.1)"),
)
@click.option(
    "--port",
    type=click.IntRange(min=1, max=65535),
    default=8000,
    help=_("Port to bind to (default: 8000, range: 1-65535)"),
)
@click.option(
    "--reload",
    is_flag=True,
    help=_("Enable auto-reload for development (watches for file changes)"),
)
@click.option(
    "--log-file",
    type=click.Path(path_type=Path),
    help=_("Path to log file (enables file-based logging with rotation)"),
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help=_("Enable verbose logging"),
)
@click.help_option("-h", "--help")
def serve(host: str, port: int, reload: bool, log_file: Path | None, verbose: bool) -> None:
    r"""Start web interface server.

    Starts a FastAPI web server providing browser-based access to
    NHL Scrabble analysis. Visit http://localhost:8000 after starting.

    \b
    Examples:
      Start server on default port (8000):
        $ nhl-scrabble serve

      Development mode with auto-reload:
        $ nhl-scrabble serve --reload

      Custom host and port:
        $ nhl-scrabble serve --host 0.0.0.0 --port 5000

      Bind to all interfaces on custom port:
        $ nhl-scrabble serve --host 0.0.0.0 --port 3000 --reload

      Enable file-based logging:
        $ nhl-scrabble serve --log-file logs/server.log

      Enable verbose logging with file output:
        $ nhl-scrabble serve --verbose --log-file logs/debug.log

      Combine multiple options:
        $ nhl-scrabble serve --host 0.0.0.0 --port 5000 --reload --log-file logs/dev.log
    """
    try:
        import uvicorn
    except ImportError:
        click.echo(
            "Error: uvicorn not installed. Install with: pip install nhl-scrabble[web]",
            err=True,
        )
        raise click.Abort from None

    # Load configuration for logging settings
    try:
        config = Config.from_env()
    except ValueError as e:
        raise click.ClickException(f"Configuration error: {e}") from e

    # Setup logging with optional file output
    setup_logging(
        verbose=verbose,
        sanitize_logs=config.sanitize_logs,
        log_file=log_file,
        max_bytes=config.log_max_bytes,
        backup_count=config.log_backup_count,
    )

    click.echo(f"Starting NHL Scrabble web server at http://{host}:{port}")
    if log_file:
        click.echo(f"Logging to: {log_file}")
    click.echo("Press CTRL+C to stop")

    # When reload is enabled, pass import string for uvicorn to reload properly
    # When reload is disabled, import app directly for faster startup
    if reload:
        uvicorn.run(
            "nhl_scrabble.web.app:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info",
        )
    else:
        # Import here to avoid loading FastAPI when not needed
        from nhl_scrabble.web.app import app

        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=reload,
            log_level="info",
        )
