import logging

from motor.motor_asyncio import AsyncIOMotorClient

from src.app.core.config import settings

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    async def connect(cls):
        try:
            cls.client = AsyncIOMotorClient(settings.MONGO_URI)
            cls.db = cls.client[settings.MONGO_DB]
            logger.info(f"Connected to the database: {settings.MONGO_DB}")
        except Exception as e:
            logger.error(f"An error occurred while connecting to the database: {e}")

    @classmethod
    async def disconnect(cls):
        if cls.client:
            cls.client.close()

    @classmethod
    def get_collection(cls, collection_name: str):
        return cls.db[collection_name]

database = Database()