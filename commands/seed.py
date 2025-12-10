"""Command to seed Formbricks with generated data."""

import json
from pathlib import Path
from typing import Dict, Any, List
from api import FormbricksClient
from generators import DataGenerator
from utils.config import get_config
from utils.logger import info, success, error, section, warning, create_progress
import time


def seed_command() -> None:
    """Seed Formbricks with generated data using APIs."""
    section("Seeding Formbricks with Data")

    # Validate configuration
    try:
        config = get_config()
        config.validate_required_for_seed()
    except ValueError as e:
        error(str(e))
        info("\nPlease ensure you have:")
        info("1. Started Formbricks (python main.py formbricks up)")
        info("2. Created an account at http://localhost:3000")
        info("3. Generated an API key in Settings > API Keys")
        info("4. Updated .env with FORMBRICKS_API_KEY, ORGANIZATION_ID, and ENVIRONMENT_ID")
        return

    # Load generated data
    data_file = config.data_dir / "generated_data.json"
    if not data_file.exists():
        error(f"Generated data not found at {data_file}")
        info("Please run: python main.py formbricks generate")
        return

    try:
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        error(f"Failed to load generated data: {e}")
        return

    surveys_data = data.get("surveys", [])
    users_data = data.get("users", [])

    if not surveys_data or not users_data:
        error("Generated data is incomplete. Please regenerate.")
        return

    # Initialize API client
    client = FormbricksClient(
        base_url=config.formbricks_url,
        api_key=config.api_key,
        organization_id=config.organization_id,
        environment_id=config.environment_id
    )

    # Verify connection
    info("Verifying API connection...")
    if not client.health_check():
        error("Cannot connect to Formbricks. Is it running?")
        info("Run: python main.py formbricks up")
        return

    try:
        account_info = client.verify_auth()
        success(f"Connected as: {account_info.get('name', 'Unknown')}")
    except Exception as e:
        error(f"Authentication failed: {e}")
        info("Please check your API key in .env file")
        return

    # Seed users
    section("\nSeeding Users")
    info(f"Creating {len(users_data)} users...")

    created_users = []
    for idx, user in enumerate(users_data, 1):
        try:
            result = client.create_user(
                name=user["name"],
                email=user["email"],
                role=user["role"]
            )
            created_users.append(result)
            success(f"  [{idx}/{len(users_data)}] Created: {user['name']} ({user['role']})")
            time.sleep(0.5)  # Rate limiting
        except Exception as e:
            warning(f"  [{idx}/{len(users_data)}] Failed to create {user['name']}: {e}")

    success(f"\nCreated {len(created_users)}/{len(users_data)} users")

    # Seed surveys
    section("\nSeeding Surveys")
    info(f"Creating {len(surveys_data)} surveys...")

    created_surveys = []
    for idx, survey in enumerate(surveys_data, 1):
        try:
            result = client.create_survey(survey)
            created_surveys.append(result)
            success(f"  [{idx}/{len(surveys_data)}] Created: {survey.get('name', 'Unnamed')}")
            time.sleep(0.5)  # Rate limiting
        except Exception as e:
            warning(f"  [{idx}/{len(surveys_data)}] Failed to create survey: {e}")

    success(f"\nCreated {len(created_surveys)}/{len(surveys_data)} surveys")

    if not created_surveys:
        error("No surveys were created. Cannot proceed with responses.")
        return

    # Generate and seed responses
    section("\nSeeding Survey Responses")
    info("Generating realistic responses...")

    try:
        config.validate_required_for_generate()
        generator = DataGenerator(
            api_key=config.openai_api_key,
            model=config.openai_model
        )
        has_generator = True
    except ValueError:
        warning("OpenAI API key not configured. Using basic responses.")
        has_generator = False

    total_responses = 0
    for idx, survey_result in enumerate(created_surveys, 1):
        survey_id = survey_result.get("id")
        survey_name = survey_result.get("name", "Unnamed")

        if not survey_id:
            continue

        info(f"  [{idx}/{len(created_surveys)}] Creating response for: {survey_name}")

        try:
            # Generate realistic response using LLM if available
            if has_generator:
                responses = generator.generate_responses(survey_result, count=1)
            else:
                # Fallback: Create basic response
                responses = [_create_basic_response(survey_result)]

            # Submit response
            for response_data in responses:
                try:
                    client.create_response(survey_id, response_data)
                    total_responses += 1
                    success(f"    ✓ Response created")
                    time.sleep(0.5)
                except Exception as e:
                    warning(f"    ✗ Failed to create response: {e}")

        except Exception as e:
            warning(f"  Failed to generate response for {survey_name}: {e}")

    success(f"\nCreated {total_responses} survey responses")

    # Summary
    section("\nSeeding Complete!")
    info(f"✓ Users created: {len(created_users)}")
    info(f"✓ Surveys created: {len(created_surveys)}")
    info(f"✓ Responses created: {total_responses}")

    info(f"\nView your data at: {config.formbricks_url}")


def _create_basic_response(survey: Dict[str, Any]) -> Dict[str, Any]:
    """Create a basic response when LLM is not available.

    Args:
        survey: Survey configuration

    Returns:
        Basic response data
    """
    data = {}

    for question in survey.get("questions", []):
        q_id = question.get("id")
        q_type = question.get("type")

        if not q_id:
            continue

        # Generate simple answers based on type
        if q_type == "openText":
            data[q_id] = "This is a sample response"
        elif q_type == "multipleChoiceSingle":
            choices = question.get("choices", [])
            if choices:
                data[q_id] = choices[0].get("label", {}).get("default", "")
        elif q_type == "multipleChoiceMulti":
            choices = question.get("choices", [])
            if choices:
                data[q_id] = [choices[0].get("label", {}).get("default", "")]
        elif q_type == "nps":
            data[q_id] = 8
        elif q_type == "rating":
            range_val = question.get("range", 5)
            data[q_id] = range_val - 1

    return {
        "finished": True,
        "data": data,
        "meta": {
            "source": "Automated Seeding",
            "url": "http://localhost:3000"
        }
    }
