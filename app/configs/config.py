from motor.motor_asyncio import AsyncIOMotorClient
# binary encoding/decvoding
from bson.objectid import ObjectId
from beanie import init_beanie

from app.models.temple import Temple



from pydantic import BaseSettings

class Settings(BaseSettings):
    # database configurations
    DATABASE_URL: str = None

    class Config:
        env_file = ".env"
        orm_mode = True

async def initialDatabase():
    client = AsyncIOMotorClient(Settings().DATABASE_URL)
    await init_beanie(database=client.get_default_database() , document_models=[Temple])
    