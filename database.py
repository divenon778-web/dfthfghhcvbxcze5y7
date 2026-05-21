import os
import redis
import string
import random

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

ADMIN_KEY = "9001"

def is_valid_key(user_key: str) -> bool:
    return redis_client.exists(f"vain_key:{user_key}")

def generate_key(duration_days: int = 0) -> str:
    chars = string.ascii_letters + string.digits
    key = ''.join(random.choices(chars, k=16))
    redis_client.set(f"vain_key:{key}", "active")
    if duration_days > 0:
        redis_client.expire(f"vain_key:{key}", duration_days * 86400)
    return key

def check_admin(admin_key: str) -> bool:
    return admin_key == ADMIN_KEY
