"""Command to start Formbricks locally."""

import subprocess
import time
import requests
from pathlib import Path
from utils.logger import info, success, error, section, create_progress


def up_command() -> None:
    """Start Formbricks using Docker Compose."""
    section("Starting Formbricks")

    project_root = Path(__file__).parent.parent
    compose_file = project_root / "docker-compose.yml"

    if not compose_file.exists():
        error(f"docker-compose.yml not found at {compose_file}")
        return

    info("Starting Docker Compose services...")

    try:
        # Start services
        subprocess.run(
            ["docker-compose", "up", "-d"],
            cwd=project_root,
            check=True,
            capture_output=True
        )

        success("Docker Compose services started")

        # Wait for Formbricks to be healthy
        info("Waiting for Formbricks to be ready...")

        formbricks_url = "http://localhost:3000"
        max_attempts = 60
        attempt = 0

        with create_progress() as progress:
            task = progress.add_task("Checking health...", total=None)

            while attempt < max_attempts:
                try:
                    response = requests.get(f"{formbricks_url}/api/health", timeout=2)
                    if response.status_code == 200:
                        progress.stop()
                        break
                except:
                    pass

                attempt += 1
                time.sleep(2)

        if attempt >= max_attempts:
            error("Formbricks failed to start within the expected time")
            info("Check logs with: docker-compose logs -f")
            return

        success(f"Formbricks is ready at {formbricks_url}")

        # Display next steps
        info("\nNext steps:")
        info("1. Open http://localhost:3000 in your browser")
        info("2. Create an account and sign in")
        info("3. Go to Settings > API Keys to generate an API key")
        info("4. Copy your Organization ID and Environment ID from the URL")
        info("5. Update your .env file with these credentials")
        info("6. Run: python main.py formbricks generate")
        info("7. Run: python main.py formbricks seed")

    except subprocess.CalledProcessError as e:
        error(f"Failed to start Docker Compose: {e}")
        if e.stderr:
            error(e.stderr.decode())
    except Exception as e:
        error(f"Unexpected error: {e}")
