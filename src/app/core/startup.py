from collections.abc import Callable
from contextlib import AbstractContextManager, asynccontextmanager
from typing import Any

from fastapi import FastAPI, APIRouter

from src.app.core.config import AppSettings, EnvironmentSettings
from src.app.core.db.database import database


# --------------------------- database ---------------------------
async def connect_to_db():
    await database.connect()

async def disconnect_from_db():
    await database.disconnect()

# --------------------------- application ---------------------------
def lifespan_factory(
        settings: AppSettings | EnvironmentSettings,
) -> Callable[[FastAPI], AbstractContextManager[Any]]:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await connect_to_db()
        yield
        await disconnect_from_db()

    return lifespan

def create_application(
        router: APIRouter,
        settings: AppSettings | EnvironmentSettings,
        **kwargs: Any,
) -> FastAPI:
    if isinstance(settings, AppSettings):
        kwargs.update({"title": settings.APP_NAME, "description": settings.APP_DESCRIPTION})

    lifespan = lifespan_factory(settings)

    application = FastAPI(lifespan=lifespan, **kwargs)
    application.include_router(router)

    return application