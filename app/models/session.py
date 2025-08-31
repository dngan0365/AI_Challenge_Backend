from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class SessionResponse(BaseModel):
    session_id: UUID
    created_at: datetime

class AllSessionsResponse(BaseModel):
    session_id: UUID
    created_at: datetime
    last_updated: datetime