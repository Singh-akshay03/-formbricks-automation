"""Command to generate realistic survey data using LLMs."""

from pathlib import Path
from generators import DataGenerator
from utils.config import get_config
from utils.logger import info, success, error, section, create_progress


def generate_command() -> None:
    """Generate realistic survey data using OpenAI."""
    section("Generating Realistic Data")

    try:
        config = get_config()
        config.validate_required_for_generate()
    except ValueError as e:
        error(str(e))
        info("Please set OPENAI_API_KEY in your .env file")
        return

    try:
        generator = DataGenerator(
            api_key=config.openai_api_key,
            model=config.openai_model
        )

        # Ensure data directory exists
        config.data_dir.mkdir(exist_ok=True)

        # Generate surveys
        info("Generating 5 unique surveys...")
        with create_progress() as progress:
            task = progress.add_task("Creating surveys...", total=None)
            surveys = generator.generate_surveys(count=5)
            progress.stop()

        success(f"Generated {len(surveys)} surveys")

        # Generate users
        info("Generating 10 users...")
        with create_progress() as progress:
            task = progress.add_task("Creating users...", total=None)
            users = generator.generate_users(count=10)
            progress.stop()

        success(f"Generated {len(users)} users")

        # Save to files
        data = {
            "surveys": surveys,
            "users": users
        }

        output_file = config.data_dir / "generated_data.json"
        generator.save_to_file(data, output_file)

        success(f"\nData saved to: {output_file}")

        # Display summary
        info("\nGenerated data summary:")
        info(f"  - Surveys: {len(surveys)}")
        for survey in surveys:
            info(f"    • {survey.get('name', 'Unnamed Survey')} ({len(survey.get('questions', []))} questions)")
        info(f"  - Users: {len(users)}")

        info("\nNext step: Run 'python main.py formbricks seed' to populate Formbricks")

    except Exception as e:
        error(f"Failed to generate data: {e}")
        import traceback
        traceback.print_exc()
