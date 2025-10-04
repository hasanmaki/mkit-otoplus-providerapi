"""settings Loader and validator using pydantic_settings.

settings ini akan di store pada app state.settings untuk di akses pada seluruh bagian aplikasi.
"""

# ruff: noqa
from functools import lru_cache


from src.config.cfg_api_clients import DigiposConfig
from pydantic_settings import BaseSettings, SettingsConfigDict, TomlConfigSettingsSource


class AppSettings(BaseSettings):
    """application settings merged from here."""

    digipos: DigiposConfig
    # isimple: IsimpleConfig

    model_config = SettingsConfigDict(
        toml_file="config.toml",
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
    return AppSettings()  # type: ignore


# buat overide if we need misal testing
def load_test_settings(path: str) -> AppSettings:
    """For testing — load without caching."""
    AppSettings.model_config["toml_file"] = path
    return AppSettings()  # type: ignore
