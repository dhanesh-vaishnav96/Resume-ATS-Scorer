import json
import hashlib
import redis.asyncio as redis
from app.config import settings
from app.utils.logger import logger

class CacheManager:
    def __init__(self):
        self.client = redis.from_url(settings.REDIS_URL, decode_responses=True)

    def _get_hash(self, text: str) -> str:
        return hashlib.md5(text.lower().strip().encode()).hexdigest()

    async def get_jd_skills(self, jd_text: str) -> set:
        """Retrieve skills from cache if they exist."""
        try:
            key = f"jd_skills:{self._get_hash(jd_text)}"
            cached = await self.client.get(key)
            if cached:
                logger.info("Cache hit for JD skills.")
                return set(json.loads(cached))
            return None
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
            return None

    async def set_jd_skills(self, jd_text: str, skills: set, ttl: int = 3600):
        """Cache extracted skills for a JD."""
        try:
            key = f"jd_skills:{self._get_hash(jd_text)}"
            await self.client.set(key, json.dumps(list(skills)), ex=ttl)
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")

cache_manager = CacheManager()
