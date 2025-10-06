"""settings Loader and validator using pydantic_settings.

settings ini akan di store pada app state.settings untuk di akses pada seluruh bagian aplikasi.
"""

# ruff: noqa
from functools import lru_cache
from pathlib import Path


from src.config.cfg_api_clients import DigiposConfig
from pydantic_settings import BaseSettings, SettingsConfigDict, TomlConfigSettingsSource
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_FILE = "config.toml"
CONFIG_PATH = BASE_DIR / CONFIG_FILE


class CoreAppSettings(BaseModel):
    """Core application settings."""

    name: str = "mkit-otoplus-providerapi"
    version: str = "0.1.0"
    description: str = "API Gateway for Otoplus Provider Integrations"
    environment: str = "development"
    log_level: str = "INFO"


class AppSettings(BaseSettings):
    """application settings merged from here."""

    application: CoreAppSettings = Field(default_factory=CoreAppSettings)
    digipos: DigiposConfig
    # isimple: IsimpleConfig

    model_config = SettingsConfigDict(
        toml_file=CONFIG_PATH,
        extra="forbid",
        validate_assignment=True,
        from_attributes=True,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ) -> tuple[TomlConfigSettingsSource, ...]:
        return (TomlConfigSettingsSource(settings_cls),)


@lru_cache
def get_settings() -> AppSettings:
    # check file first
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config file not found: {CONFIG_PATH}")

    return AppSettings()  # type: ignore


# buat overide if we need misal testing
def load_test_settings(path: str) -> AppSettings:
    """For testing — load without caching."""
    AppSettings.model_config["toml_file"] = path
    return AppSettings()  # type: ignore
