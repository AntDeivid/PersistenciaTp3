from motor.motor_asyncio import AsyncIOMotorClient

from src.app.core.config import settings


class Database:
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    async def connect(cls):
        try:
            cls.client = AsyncIOMotorClient(settings.MONGO_URI)
            cls.db = cls.client[settings.MONGO_DB]
        except Exception as e:
            print(f"An error occurred while connecting to the database: {e}")

    @classmethod
    async def disconnect(cls):
        if cls.client:
            cls.client.close()

database = Database()