"""Command to stop Formbricks."""

import subprocess
from pathlib import Path
from utils.logger import info, success, error, section


def down_command() -> None:
    """Stop Formbricks and clean up Docker resources."""
    section("Stopping Formbricks")

    project_root = Path(__file__).parent.parent
    compose_file = project_root / "docker-compose.yml"

    if not compose_file.exists():
        error(f"docker-compose.yml not found at {compose_file}")
        return

    info("Stopping Docker Compose services...")

    try:
        # Stop and remove containers
        subprocess.run(
            ["docker-compose", "down"],
            cwd=project_root,
            check=True,
            capture_output=True
        )

        success("Docker Compose services stopped")

        info("\nNote: Data volumes are preserved. To remove all data, run:")
        info("docker-compose down -v")

    except subprocess.CalledProcessError as e:
        error(f"Failed to stop Docker Compose: {e}")
        if e.stderr:
            error(e.stderr.decode())
    except Exception as e:
        error(f"Unexpected error: {e}")
