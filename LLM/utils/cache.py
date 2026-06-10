from cachetools import TTLCache

# Create a shared cache instance
# - maxsize: The maximum number of items the cache can hold
# - ttl: The time-to-live for each item in seconds
cache = TTLCache(maxsize=1000, ttl=3600)
