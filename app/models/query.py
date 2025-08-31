from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from uuid import UUID

class QueryRequest(BaseModel):
    text_query: Optional[str] = None
    image_query: Optional[str] = None
    od_json: Optional[str] = None   # or Dict[str, Any] if it's JSON
    ocr_text: Optional[str] = None
    asr_text: Optional[str] = None

class QueryResult(BaseModel):
    keyframe_id: UUID
    video_id: str
    frame_number: int
    timestamp_ms: int
    image_url: str
    metadata: Dict[str, Any]   # safer than `dict`
    rank: int
    score: float

class QueryResponse(BaseModel):
    query_id: UUID
    session_id: UUID
    results: List[QueryResult]
