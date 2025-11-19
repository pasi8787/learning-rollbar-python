"""Configuration module for application settings."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_APP_ROOT = Path(__file__).parent.parent.parent
_ENV_FILE = _APP_ROOT / ".env"


class ApplicationEnvironment(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
        cli_parse_args=True,
    )

    name: str = Field(default="local", validation_alias="ENVIRONMENT")

    @property
    def root_path(self) -> Path:
        return _APP_ROOT

    def from_root(self, relative_path: Path | str) -> Path:
        return _APP_ROOT / relative_path


app_environment = ApplicationEnvironment()
print(f"ENVIRONMENT={app_environment.name}")
