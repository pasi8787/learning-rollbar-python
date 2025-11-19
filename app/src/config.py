"""Configuration module for application settings."""

import subprocess

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

from .environment import app_environment


class RollbarSettings(BaseModel):
    access_token: str = Field(description="Rollbar access token")
    code_version: str = Field(default="")

    @field_validator("code_version", mode="before")
    @classmethod
    def not_empty_value_or_git_commit(cls, value: str) -> str:
        """Auto-detect git commit hash if not explicitly set."""
        if value:
            return value

        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
                timeout=5,
                cwd=app_environment.root_path,
            )
            return result.stdout.strip()
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ):
            return "unknown"


class ApplicationSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(app_environment.from_root(".env")),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    rollbar: RollbarSettings = Field(description="Rollbar settings")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            env_settings,
            dotenv_settings,
            YamlConfigSettingsSource(
                settings_cls,
                app_environment.from_root(f"settings.{app_environment.name}.yaml"),
            ),
            YamlConfigSettingsSource(
                settings_cls,
                app_environment.from_root("settings.yaml"),
            ),
            init_settings,
        )


app_settings = ApplicationSettings()
