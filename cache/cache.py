from cachetools import TTLCache

# Shared cache instance for plans
cache = TTLCache(maxsize=100, ttl=3600)
