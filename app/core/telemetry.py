import asyncio
from typing import Dict, Set
import json
import time

class TelemetryManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TelemetryManager, cls).__new__(cls)
            cls._instance.subscribers: Set[asyncio.Queue] = set()
        return cls._instance

    async def emit(self, event_type: str, message: str, details: dict = None):
        """Broadcast a telemetry packet to all connected listeners."""
        packet = {
            "timestamp": time.time(),
            "type": event_type,
            "message": message,
            "details": details or {}
        }
        
        # Dispatch to all active queues
        if self.subscribers:
            data = f"data: {json.dumps(packet)}\n\n"
            for queue in self.subscribers:
                await queue.put(data)

    async def subscribe(self):
        """Yield a new telemetry queue for an SSE stream."""
        queue = asyncio.Queue()
        self.subscribers.add(queue)
        try:
            while True:
                yield await queue.get()
        finally:
            self.subscribers.remove(queue)

telemetry = TelemetryManager()
