#!/usr/bin/env python3
"""Verify that the Formbricks automation tool is set up correctly."""

import sys
import subprocess
from pathlib import Path


def check_command(cmd: str, name: str) -> bool:
    """Check if a command is available."""
    try:
        subprocess.run(
            cmd.split(),
            capture_output=True,
            check=True,
            timeout=5
        )
        print(f"[OK] {name} is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        print(f"[FAIL] {name} is NOT installed")
        return False


def check_python_import(module: str) -> bool:
    """Check if a Python module can be imported."""
    try:
        __import__(module)
        print(f"[OK] {module} is installed")
        return True
    except ImportError:
        print(f"[FAIL] {module} is NOT installed")
        return False


def check_file(path: Path) -> bool:
    """Check if a file exists."""
    if path.exists():
        print(f"[OK] {path.name} exists")
        return True
    else:
        print(f"[FAIL] {path.name} does NOT exist")
        return False


def main():
    """Run all verification checks."""
    print("Formbricks Automation Tool - Setup Verification\n")

    all_good = True

    # Check system commands
    print("Checking system dependencies...")
    all_good &= check_command("docker --version", "Docker")
    all_good &= check_command("docker-compose --version", "Docker Compose")
    all_good &= check_command("python --version", "Python")

    print("\nChecking Python packages...")
    packages = ["click", "requests", "dotenv", "openai", "pydantic", "yaml", "rich"]
    for package in packages:
        # Handle special cases
        import_name = "python_dotenv" if package == "dotenv" else package
        import_name = "pyyaml" if package == "yaml" else import_name
        all_good &= check_python_import(import_name)

    print("\nChecking project files...")
    project_root = Path(__file__).parent
    files = [
        project_root / "main.py",
        project_root / "requirements.txt",
        project_root / "docker-compose.yml",
        project_root / ".env.example",
        project_root / "README.md",
    ]
    for file in files:
        all_good &= check_file(file)

    print("\nChecking project structure...")
    dirs = ["commands", "api", "generators", "utils", "data"]
    for dir_name in dirs:
        dir_path = project_root / dir_name
        if dir_path.exists() and dir_path.is_dir():
            print(f"[OK] {dir_name}/ directory exists")
        else:
            print(f"[FAIL] {dir_name}/ directory does NOT exist")
            all_good = False

    # Check .env file
    print("\nChecking configuration...")
    env_file = project_root / ".env"
    if env_file.exists():
        print("[OK] .env file exists")
        with open(env_file, "r") as f:
            content = f.read()
            if "OPENAI_API_KEY" in content:
                print("[OK] .env contains OPENAI_API_KEY")
            else:
                print("[WARN] .env missing OPENAI_API_KEY")
    else:
        print("[WARN] .env file does NOT exist (copy from .env.example)")

    # Summary
    print("\n" + "="*50)
    if all_good:
        print("[OK] All checks passed! You're ready to go.")
        print("\nNext steps:")
        print("1. Add your OpenAI API key to .env")
        print("2. Run: python main.py formbricks up")
    else:
        print("[FAIL] Some checks failed. Please install missing dependencies.")
        print("\nTo install Python packages:")
        print("  pip install -r requirements.txt")
        print("\nFor other dependencies, check SETUP.md")
        sys.exit(1)


if __name__ == "__main__":
    main()
