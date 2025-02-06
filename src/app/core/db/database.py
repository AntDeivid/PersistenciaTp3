import logging

from motor.motor_asyncio import AsyncIOMotorClient

from src.app.core.config import settings

logger = logging.getLogger('app_logger.startup')

class Database:
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    async def connect(cls):
        try:
            cls.client = AsyncIOMotorClient(settings.MONGO_URI)
            cls.db = cls.client[settings.MONGO_DB]
            logger.info("Connected to the database")
        except Exception as e:
            logger.error(f"Error connecting to the database: {e}")

    @classmethod
    async def disconnect(cls):
        if cls.client:
            cls.client.close()

    @classmethod
    def get_collection(cls, collection_name: str):
        return cls.db[collection_name]

database = Database()