import os
import json
import aioredis
from typing import Optional, Any
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

class RedisClient:
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None

    async def connect(self):
        """Initialize Redis connection"""
        self.redis = aioredis.from_url(REDIS_URL, decode_responses=True)

    async def disconnect(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()

    async def get(self, key: str) -> Optional[str]:
        """Get value by key"""
        if not self.redis:
            await self.connect()
        return await self.redis.get(key)

    async def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """Set key-value pair with optional expiration in seconds"""
        if not self.redis:
            await self.connect()
        return await self.redis.set(key, value, ex=expire)

    async def delete(self, key: str) -> int:
        """Delete key"""
        if not self.redis:
            await self.connect()
        return await self.redis.delete(key)

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.redis:
            await self.connect()
        return await self.redis.exists(key)

    async def incr(self, key: str) -> int:
        """Increment counter"""
        if not self.redis:
            await self.connect()
        return await self.redis.incr(key)

    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for key"""
        if not self.redis:
            await self.connect()
        return await self.redis.expire(key, seconds)

    async def ttl(self, key: str) -> int:
        """Get time to live for key"""
        if not self.redis:
            await self.connect()
        return await self.redis.ttl(key)

    async def hset(self, name: str, mapping: dict) -> int:
        """Set hash fields"""
        if not self.redis:
            await self.connect()
        return await self.redis.hset(name, mapping=mapping)

    async def hget(self, name: str, key: str) -> Optional[str]:
        """Get hash field value"""
        if not self.redis:
            await self.connect()
        return await self.redis.hget(name, key)

    async def hgetall(self, name: str) -> dict:
        """Get all hash fields"""
        if not self.redis:
            await self.connect()
        return await self.redis.hgetall(name)

    async def hdel(self, name: str, *keys: str) -> int:
        """Delete hash fields"""
        if not self.redis:
            await self.connect()
        return await self.redis.hdel(name, *keys)

    # Session management methods
    async def store_session(self, session_id: str, session_data: dict, expire_seconds: int = 3600):
        """Store session data"""
        session_key = f"session:{session_id}"
        session_json = json.dumps(session_data, default=str)
        await self.set(session_key, session_json, expire_seconds)

    async def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data"""
        session_key = f"session:{session_id}"
        session_json = await self.get(session_key)
        if session_json:
            return json.loads(session_json)
        return None

    async def delete_session(self, session_id: str):
        """Delete session"""
        session_key = f"session:{session_id}"
        await self.delete(session_key)

    async def extend_session(self, session_id: str, expire_seconds: int = 3600):
        """Extend session expiration"""
        session_key = f"session:{session_id}"
        await self.expire(session_key, expire_seconds)

    # Rate limiting methods
    async def check_rate_limit(self, identifier: str, limit: int, window_seconds: int) -> tuple[bool, int, int]:
        """
        Check rate limit for identifier
        Returns: (is_allowed, current_count, time_until_reset)
        """
        key = f"rate_limit:{identifier}"
        current_count = await self.incr(key)
        
        if current_count == 1:
            # First request in window, set expiration
            await self.expire(key, window_seconds)
            return True, current_count, window_seconds
        
        ttl = await self.ttl(key)
        if ttl == -1:
            # Key exists but no expiration, reset it
            await self.expire(key, window_seconds)
            ttl = window_seconds
        
        is_allowed = current_count <= limit
        return is_allowed, current_count, ttl

    async def reset_rate_limit(self, identifier: str):
        """Reset rate limit for identifier"""
        key = f"rate_limit:{identifier}"
        await self.delete(key)

# Global Redis client instance
redis_client = RedisClient()

async def get_redis() -> RedisClient:
    """Dependency to get Redis client"""
    if not redis_client.redis:
        await redis_client.connect()
    return redis_client