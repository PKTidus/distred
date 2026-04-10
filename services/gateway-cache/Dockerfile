FROM redis:latest

# Expose the default Redis port
EXPOSE 6379

# By default, run Redis with AOF (Append Only File) persistence enabled.
# This makes it behave more like a permanent cache.
CMD ["redis-server", "--appendonly", "yes"]
