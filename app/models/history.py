# app/models/history.py
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime

class HistoryResult(BaseModel):
    keyframe_id: UUID
    video_id: str          # đổi từ UUID sang str
    frame_number: int
    timestamp_ms: int
    image_url: str
    metadata: Dict[str, Any]
    rank: int
    score: float

class HistoryItem(BaseModel):
    query_id: UUID
    session_id: UUID
    text_query: Optional[str]
    image_query: Optional[str]
    od_json: Optional[str]
    ocr_text: Optional[str]
    asr_text: Optional[str]
    query_time: datetime
    results: List[HistoryResult] = []

class HistoryResponse(BaseModel):
    session_id: UUID
    queries: List[HistoryItem]
