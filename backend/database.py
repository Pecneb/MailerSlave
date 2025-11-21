"""MongoDB database connection and utilities."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from backend.config import settings
import logging

logger = logging.getLogger(__name__)

# Global database client and database objects
client: AsyncIOMotorClient = None
db: AsyncIOMotorDatabase = None


async def connect_to_mongo():
    """Connect to MongoDB."""
    global client, db
    try:
        logger.info(f"Connecting to MongoDB at {settings.mongodb_url}")
        client = AsyncIOMotorClient(settings.mongodb_url)
        db = client[settings.mongodb_database]
        
        # Verify connection
        await client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        # Create indexes
        await create_indexes()
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Close MongoDB connection."""
    global client
    if client:
        client.close()
        logger.info("Closed MongoDB connection")


async def create_indexes():
    """Create database indexes for better performance."""
    try:
        # Contacts indexes
        await db.contacts.create_index("email", unique=True)
        await db.contacts.create_index("created_at")
        
        # Templates indexes
        await db.templates.create_index("name")
        await db.templates.create_index("created_at")
        
        # Campaigns indexes
        await db.campaigns.create_index("name")
        await db.campaigns.create_index("status")
        await db.campaigns.create_index("created_at")
        
        # Email logs indexes
        await db.email_logs.create_index("campaign_id")
        await db.email_logs.create_index("contact_id")
        await db.email_logs.create_index("status")
        await db.email_logs.create_index("sent_at")
        await db.email_logs.create_index([("campaign_id", 1), ("contact_id", 1)])
        
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.warning(f"Error creating indexes: {e}")


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance."""
    return db
