import os
import redis
import string
import random

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

ADMIN_KEY = "9001"

def is_valid_key(user_key: str) -> bool:
    return redis_client.exists(f"vain_key:{user_key}")

def generate_key(key_type: str = "weekly") -> str:
    chars = string.ascii_letters + string.digits
    key = ''.join(random.choices(chars, k=16))
    ttl_map = {"weekly": 604800, "monthly": 2592000}
    ttl = ttl_map.get(key_type)
    if ttl:
        redis_client.setex(f"vain_key:{key}", ttl, "active")
    else:
        redis_client.set(f"vain_key:{key}", "active")
    return key

def check_admin(admin_key: str) -> bool:
    return admin_key == ADMIN_KEY
