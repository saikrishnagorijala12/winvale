import asyncio
import json
import logging
from typing import AsyncGenerator
from redis.asyncio import Redis
from app.config import settings

logger = logging.getLogger(__name__)

# Async Redis client for SSE
redis_async = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True,
    ssl=settings.REDIS_SSL,
    ssl_cert_reqs=None if settings.REDIS_SSL else None,
    socket_connect_timeout=settings.REDIS_SOCKET_CONNECT_TIMEOUT,
)

async def event_generator(channel: str) -> AsyncGenerator[str, None]:
    """
    Async generator that listens to a Redis channel and yields SSE formatted events.
    """
    pubsub = redis_async.pubsub()
    await pubsub.subscribe(channel)
    
    try:
        # Send an initial connect event
        yield f"data: {json.dumps({'status': 'connected', 'message': f'Subscribed to {channel}'})}\n\n"
        
        while True:
            try:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message:
                    data = message["data"]
                    yield f"data: {data}\n\n"
                
                # Periodically send a keep-alive comment
                # yield ": keep-alive\n\n"
                
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Error in SSE event generator: {e}")
                yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"
                break
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()

def format_sse_event(data: dict) -> str:
    """Helper to format a dict as a JSON string for SSE."""
    return json.dumps(data)
