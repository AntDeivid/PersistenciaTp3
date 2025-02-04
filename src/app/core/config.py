import os
from enum import Enum

from pymongo import MongoClient
from starlette.config import Config

current_file_dir = os.path.dirname(os.path.realpath(__file__))
env_path = os.path.join(current_file_dir, "..", "..", ".env")
config = Config(env_path)


class AppSettings:
    APP_NAME: str = config("APP_NAME", default="FastAPI app")
    APP_DESCRIPTION: str | None = config("APP_DESCRIPTION", default=None)
    APP_VERSION: str | None = config("APP_VERSION", default=None)

class DatabaseSettings:
    pass

class MongoSettings(DatabaseSettings):
    MONGO_USER: str = config("MONGO_USER", default="root")
    MONGO_PASSWORD: str = config("MONGO_PASSWORD", default="example")
    MONGO_SERVER: str = config("MONGO_SERVER", default="localhost")
    MONGO_PORT: int = config("MONGO_PORT", default=27017)
    MONGO_DB: str = config("MONGO_DB", default="tp3")
    MONGO_URI: str = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_SERVER}:{MONGO_PORT}/{MONGO_DB}"

class EnvironmentOption(Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class EnvironmentSettings:
    ENVIRONMENT: EnvironmentOption = config("ENVIRONMENT", default=EnvironmentOption.DEVELOPMENT)


class Settings(AppSettings, MongoSettings, EnvironmentSettings):
    pass


settings = Settings()