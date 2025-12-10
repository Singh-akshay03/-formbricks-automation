"""Configuration management for Formbricks automation."""

import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()


class Config(BaseModel):
    """Configuration settings for Formbricks automation."""

    # Formbricks settings
    formbricks_url: str = Field(default_factory=lambda: os.getenv("FORMBRICKS_URL", "http://localhost:3000"))
    api_key: str = Field(default_factory=lambda: os.getenv("FORMBRICKS_API_KEY", ""))
    organization_id: str = Field(default_factory=lambda: os.getenv("ORGANIZATION_ID", ""))
    environment_id: str = Field(default_factory=lambda: os.getenv("ENVIRONMENT_ID", ""))

    # Database settings
    postgres_password: str = Field(default_factory=lambda: os.getenv("POSTGRES_PASSWORD", "postgres"))

    # Security secrets
    nextauth_secret: str = Field(default_factory=lambda: os.getenv("NEXTAUTH_SECRET", ""))
    encryption_key: str = Field(default_factory=lambda: os.getenv("ENCRYPTION_KEY", ""))
    cron_secret: str = Field(default_factory=lambda: os.getenv("CRON_SECRET", ""))

    # OpenAI settings
    openai_api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_model: str = Field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini"))

    # Paths
    project_root: Path = Field(default_factory=lambda: Path(__file__).parent.parent)
    data_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent / "data")

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True

    def validate_required_for_seed(self) -> None:
        """Validate that required fields for seeding are present."""
        missing = []
        if not self.api_key:
            missing.append("FORMBRICKS_API_KEY")
        if not self.organization_id:
            missing.append("ORGANIZATION_ID")
        if not self.environment_id:
            missing.append("ENVIRONMENT_ID")

        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    def validate_required_for_generate(self) -> None:
        """Validate that required fields for generation are present."""
        if not self.openai_api_key:
            raise ValueError("Missing required environment variable: OPENAI_API_KEY")


def get_config() -> Config:
    """Get the configuration instance."""
    return Config()
