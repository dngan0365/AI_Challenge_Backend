from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from uuid import UUID
import json
import logging

from app.db import database

router = APIRouter()
logger = logging.getLogger(__name__)


class HistoryResult(BaseModel):
    keyframe_id: UUID
    video_id: str
    frame_number: int
    timestamp_ms: int
    image_url: str
    metadata: Dict[str, Any]
    rank: int
    score: float


def parse_metadata(meta):
    """Parse metadata safely from string to dict."""
    if isinstance(meta, str):
        try:
            return json.loads(meta)
        except json.JSONDecodeError:
            logger.warning(f"Invalid metadata JSON: {meta}")
            return {}
    return meta or {}


@router.get("/history", response_model=List[HistoryResult])
async def get_history(
    session: UUID = Query(..., description="Session ID"),
    db=Depends(database.get_db),
):
    """Get search history for a specific session."""
    try:
        # Lấy danh sách query_id theo session
        queries = await db.fetch(
            "SELECT query_id FROM queries WHERE session_id=$1 ORDER BY created_at DESC",
            session,
        )
        if not queries:
            return []

        query_ids = [q["query_id"] for q in queries]

        # Lấy kết quả từ query_results, join keyframes để lấy thêm thông tin
        results = await db.fetch(
            """
            SELECT qr.keyframe_id, k.video_id, k.frame_number, k.timestamp_ms,
                   k.image_url, k.metadata, qr.rank, qr.score
            FROM query_results qr
            JOIN keyframes k ON qr.keyframe_id = k.keyframe_id
            WHERE qr.query_id = ANY($1::uuid[])
            ORDER BY qr.rank ASC
            """,
            query_ids,
        )

        parsed_results = [
            HistoryResult(
                keyframe_id=r["keyframe_id"],
                video_id=r["video_id"],
                frame_number=r["frame_number"],
                timestamp_ms=r["timestamp_ms"],
                image_url=r["image_url"],
                metadata=parse_metadata(r["metadata"]),
                rank=r["rank"],
                score=r["score"],
            )
            for r in results
        ]
        return parsed_results

    except Exception as e:
        logger.exception(f"Error in /history: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch history")


@router.get("/history/all", response_model=List[HistoryResult])
async def get_all_history(
    db=Depends(database.get_db),
):
    """Get all search history."""
    try:
        results = await db.fetch(
            """
            SELECT qr.keyframe_id, k.video_id, k.frame_number, k.timestamp_ms,
                   k.image_url, k.metadata, qr.rank, qr.score
            FROM query_results qr
            JOIN keyframes k ON qr.keyframe_id = k.keyframe_id
            ORDER BY qr.rank ASC
            """
        )

        parsed_results = [
            HistoryResult(
                keyframe_id=r["keyframe_id"],
                video_id=r["video_id"],
                frame_number=r["frame_number"],
                timestamp_ms=r["timestamp_ms"],
                image_url=r["image_url"],
                metadata=parse_metadata(r["metadata"]),
                rank=r["rank"],
                score=r["score"],
            )
            for r in results
        ]
        return parsed_results

    except Exception as e:
        logger.exception(f"Error in /history/all: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch all history")
