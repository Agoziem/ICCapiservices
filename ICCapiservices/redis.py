from typing import Optional
import redis.asyncio as aioredis
from django.conf import settings

JTI_EXPIRY = 3600  # 1 hour

# Synchronous Redis connection
token_blocklist = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

async def add_oauth_code_to_blocklist(code: str, user_id: str) -> None:
    await token_blocklist.set(name=code, value=user_id, ex=JTI_EXPIRY)


async def oauth_code_in_blocklist(code: str) -> Optional[str]:
    user_id = await token_blocklist.get(code)
    if user_id:
        await token_blocklist.delete(code)
        return user_id
    return None
