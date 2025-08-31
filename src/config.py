from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict, SecretStr
from functools import lru_cache


class Settings(BaseSettings):

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

    ticketmaster_api_key: SecretStr = Field(..., env="TICKETMASTER_API_KEY")


@lru_cache
def get_settings():
    return config.Settings()
