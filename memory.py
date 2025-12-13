import asyncio
import json
from typing import Any, Dict

class MemoryStore:
    def __init__(self, use_mongo=False, mongo_uri=None):
        self.use_mongo = use_mongo
        self._memory:Dict[str, Any] = {}
        self._lock = asyncio.Lock()
    
    async def set(self, key: str, value: Any):
        async with self._lock:
            self._memory[key] = value
    
    async def get(self, key:str, default=None):
        return self._memory.get(key, default)

    async def append_list(self, key:str, item:Any):
        lst = self._memory.get(key, [])
        lst.append(item)
        self._memory[key] = lst
