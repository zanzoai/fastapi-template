import json
import hashlib
from typing import Any, Optional, Callable
from functools import wraps
import redis
from core.config import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_PASSWORD,
    REDIS_DB,
    REDIS_URL,
)

# Global Redis connection pool
_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> redis.Redis:
    """Get or create Redis client with connection pooling."""
    global _redis_client
    if _redis_client is None:
        if REDIS_URL:
            _redis_client = redis.from_url(
                REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
            )
        else:
            _redis_client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                password=REDIS_PASSWORD,
                db=REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
            )
        # Test connection
        try:
            _redis_client.ping()
        except redis.ConnectionError as e:
            print(f"Warning: Could not connect to Redis: {e}")
            print("Caching will be disabled. Make sure Redis is running and configured correctly.")
    return _redis_client


def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """Generate a cache key from prefix and arguments."""
    # Create a hash of the arguments for consistent key generation
    key_parts = [prefix]
    
    # Add positional arguments
    for arg in args:
        if arg is not None:
            key_parts.append(str(arg))
    
    # Add keyword arguments (sorted for consistency)
    for key, value in sorted(kwargs.items()):
        if value is not None:
            key_parts.append(f"{key}:{value}")
    
    # Create a hash if the key would be too long
    key_string = ":".join(key_parts)
    if len(key_string) > 200:  # Redis key length limit consideration
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        return f"{prefix}:hash:{key_hash}"
    
    return key_string


def cache_get(key: str) -> Optional[Any]:
    """Get value from cache."""
    try:
        client = get_redis_client()
        value = client.get(key)
        if value:
            return json.loads(value)
    except (redis.RedisError, json.JSONDecodeError) as e:
        print(f"Cache get error for key {key}: {e}")
    return None


def cache_set(key: str, value: Any, ttl: int = 300) -> bool:
    """Set value in cache with TTL."""
    try:
        client = get_redis_client()
        serialized = json.dumps(value, default=str)  # default=str handles datetime and other non-serializable types
        return client.setex(key, ttl, serialized)
    except (redis.RedisError, TypeError) as e:
        print(f"Cache set error for key {key}: {e}")
    return False


def cache_delete(key: str) -> bool:
    """Delete a key from cache."""
    try:
        client = get_redis_client()
        return bool(client.delete(key))
    except redis.RedisError as e:
        print(f"Cache delete error for key {key}: {e}")
    return False


def cache_delete_pattern(pattern: str) -> int:
    """Delete all keys matching a pattern."""
    try:
        client = get_redis_client()
        keys = client.keys(pattern)
        if keys:
            return client.delete(*keys)
    except redis.RedisError as e:
        print(f"Cache delete pattern error for pattern {pattern}: {e}")
    return 0


def invalidate_job_cache(job_id: Optional[int] = None, user_id: Optional[int] = None):
    """Invalidate job-related cache entries."""
    try:
        # Invalidate specific job detail
        if job_id:
            cache_delete(f"job:detail:{job_id}")
        
        # Invalidate jobs list
        cache_delete_pattern("job:list:*")
        
        # Invalidate user-specific jobs
        if user_id:
            cache_delete_pattern(f"job:user:{user_id}:*")
        else:
            # If no user_id specified, invalidate all user job caches
            cache_delete_pattern("job:user:*")
    except Exception as e:
        print(f"Cache invalidation error: {e}")


def cached(prefix: str, ttl: int = 300):
    """
    Decorator to cache function results.
    
    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = generate_cache_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_value = cache_get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Call the function
            result = func(*args, **kwargs)
            
            # Store in cache
            cache_set(cache_key, result, ttl)
            
            return result
        
        return sync_wrapper
    
    return decorator

