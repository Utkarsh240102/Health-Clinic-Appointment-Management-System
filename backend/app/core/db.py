from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings
from typing import Optional

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

mongodb = MongoDB()


async def connect_to_mongo():
    """Connect to MongoDB"""
    mongodb.client = AsyncIOMotorClient(settings.MONGODB_URL)
    mongodb.db = mongodb.client[settings.MONGODB_DB_NAME]
    print(f"✅ Connected to MongoDB: {settings.MONGODB_DB_NAME}")


async def close_mongo_connection():
    """Close MongoDB connection"""
    if mongodb.client:
        mongodb.client.close()
        print("❌ Closed MongoDB connection")


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    if mongodb.db is None:
        raise Exception("Database not initialized")
    return mongodb.db


# Collection getters
def get_users_collection():
    return get_database()["users"]


def get_appointments_collection():
    return get_database()["appointments"]


def get_twilio_logs_collection():
    return get_database()["twilio_logs"]
