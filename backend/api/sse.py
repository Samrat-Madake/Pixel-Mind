import asyncio
from typing import AsyncGenerator
from collections import defaultdict
import json

class SSEManager:
    def __init__(self):
        self.queues = defaultdict(list)

    async def add_event(self, channel: str, event_data: dict):
        # We drop events if there are no listeners to avoid memory leaks
        for queue in self.queues.get(channel, []):
            await queue.put(event_data)

    async def stream_events(self, channel: str) -> AsyncGenerator[str, None]:
        queue = asyncio.Queue()
        self.queues[channel].append(queue)
        try:
            while True:
                data = await queue.get()
                yield f"data: {json.dumps(data)}\n\n"
        except asyncio.CancelledError:
            self.queues[channel].remove(queue)
            if not self.queues[channel]:
                del self.queues[channel]
            raise

sse_manager = SSEManager()
