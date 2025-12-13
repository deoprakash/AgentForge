from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    from motor.motor_asyncio import AsyncIOMotorClient
    MOTOR_AVAILABLE = True
except ImportError:
    MOTOR_AVAILABLE = False

class MemoryStore:
    def __init__(self, mongo_uri: Optional[str] = None, db_name: str = "AgentForge"):
        if mongo_uri and MOTOR_AVAILABLE:
            self.client = AsyncIOMotorClient(mongo_uri)
            self.db = self.client[db_name]
            self.use_mongo = True
        else:
            self.db = None
            self.use_mongo = False
            self._memory = {}


# -------------------- Session ---------------

    async def create_session(self, goal:str, email:str):
        session = {
            "goal": goal,
            "email": email,
            "created_at": datetime.now()
        }
        if self.use_mongo:
            result = await self.db.sessions.insert_one(session)
            return str(result.inserted_id)
        else:
            session_id = f"session_{len(self._memory.get('sessions', []))}"
            if 'sessions' not in self._memory:
                self._memory['sessions'] = []
            self._memory['sessions'].append(session)
            return session_id
    
# --------------------------- Plan --------------------------

    async def save_plan(self, session_id: str, plan: Dict):
        plan["session_id"] = session_id
        plan["created_at"] = datetime.now()
        if self.use_mongo:
            await self.db.plans.insert_one(plan)
        else:
            if 'plans' not in self._memory:
                self._memory['plans'] = []
            self._memory['plans'].append(plan)

# ----------------------- Research -------------------------

    async def save_research(self, session_id:str, research: Dict):
        research["session_id"] = session_id
        research["created_at"] = datetime.now()
        if self.use_mongo:
            await self.db.research.insert_one(research)
        else:
            if 'research' not in self._memory:
                self._memory['research'] = []
            self._memory['research'].append(research)

    async def get_research(self, session_id: str) -> List[Dict]:
        if self.use_mongo:
            return await self.db.research.find(
                {"session_id": session_id}
            ).to_list(length=100)
        else:
            return [r for r in self._memory.get('research', []) if r.get('session_id') == session_id]

# ------------------- Documents ----------------------------

    async def save_document(self, session_id: str, document: Dict):
        document["session_id"] = session_id
        document["created_at"] = datetime.now()
        if self.use_mongo:
            await self.db.document.insert_one(document)
        else:
            if 'documents' not in self._memory:
                self._memory['documents'] = []
            self._memory['documents'].append(document)
    
    async def get_latest_document(self, session_id:str):
        if self.use_mongo:
            return await self.db.document.find_one(
                {"session_id": session_id},
                sort=[("created_at", -1)]
            )
        else:
            docs = [d for d in self._memory.get('documents', []) if d.get('session_id') == session_id]
            return docs[-1] if docs else None

# --------------------- Actions ------------------------------ 

    async def save_actions(self, session_id:str, action:Dict):
        action["session_id"] = session_id
        action["created_at"] = datetime.now()
        if self.use_mongo:
            await self.db.actions.insert_one(action)
        else:
            if 'actions' not in self._memory:
                self._memory['actions'] = []
            self._memory['actions'].append(action)


        