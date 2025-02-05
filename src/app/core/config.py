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
    MONGO_CLUSTER: str = config("MONGO_CLUSTER", default="localhost")
    MONGO_DB: str = config("MONGO_DB", default="tp3")
    MONGO_URI: str = config("MONGO_URI", default=f"mongodb+srv://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_CLUSTER}/{MONGO_DB}?retryWrites=true&w=majority")

class EnvironmentOption(Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class EnvironmentSettings:
    ENVIRONMENT: EnvironmentOption = config("ENVIRONMENT", default=EnvironmentOption.DEVELOPMENT)


class Settings(AppSettings, MongoSettings, EnvironmentSettings):
    pass


settings = Settings()