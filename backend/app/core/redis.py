import redis.asyncio as redis
from app.core.config import settings

redis_client = None

async def get_redis_client():
    """
    Returns the Redis client.
    Initializes it if it hasn't been initialized yet.
    """
    global redis_client
    if redis_client is None:
        redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
    return redis_client

async def close_redis_connection():
    """
    Closes the Redis connection if it exists.
    """
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None

# Example of how to use it in startup/shutdown events if needed later in main.py
# async def startup_event():
#     app.state.redis = await get_redis_client()

# async def shutdown_event():
#     await close_redis_connection()

# For direct use:
# client = await get_redis_client()
# await client.set("mykey", "myvalue")
# value = await client.get("mykey")
