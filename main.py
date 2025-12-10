#!/usr/bin/env python3
"""Formbricks Automation CLI - Manage and seed Formbricks instances."""

import sys
import click
from commands import up_command, down_command, generate_command, seed_command
from utils.logger import error, panel


@click.group()
def cli():
    """Formbricks Automation Tool - Manage and seed Formbricks instances."""
    pass


@cli.group()
def formbricks():
    """Formbricks management commands."""
    pass


@formbricks.command("up")
def up():
    """Start Formbricks locally using Docker Compose."""
    try:
        up_command()
    except KeyboardInterrupt:
        error("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        error(f"Command failed: {e}")
        sys.exit(1)


@formbricks.command("down")
def down():
    """Stop Formbricks and clean up Docker resources."""
    try:
        down_command()
    except KeyboardInterrupt:
        error("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        error(f"Command failed: {e}")
        sys.exit(1)


@formbricks.command("generate")
def generate():
    """Generate realistic survey data using LLMs."""
    try:
        generate_command()
    except KeyboardInterrupt:
        error("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        error(f"Command failed: {e}")
        sys.exit(1)


@formbricks.command("seed")
def seed():
    """Seed Formbricks with generated data using APIs."""
    try:
        seed_command()
    except KeyboardInterrupt:
        error("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        error(f"Command failed: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    if len(sys.argv) == 1:
        panel(
            "Formbricks Automation Tool\n\n"
            "Commands:\n"
            "  python main.py formbricks up        - Start Formbricks locally\n"
            "  python main.py formbricks down      - Stop Formbricks\n"
            "  python main.py formbricks generate  - Generate data using LLMs\n"
            "  python main.py formbricks seed      - Seed Formbricks with data\n\n"
            "Run 'python main.py formbricks --help' for more information.",
            title="Welcome",
            style="cyan"
        )
        sys.exit(0)

    cli()


if __name__ == "__main__":
    main()
