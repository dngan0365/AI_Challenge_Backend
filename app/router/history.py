# app/api/history.py
from fastapi import APIRouter, Depends, Query, HTTPException
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncConnection
from typing import Dict, List

from app.db import database
from app.models.history import HistoryResponse, HistoryItem, HistoryResult

router = APIRouter()

@router.get("/history", response_model=HistoryResponse)
async def get_history(session: UUID, db=Depends(database.get_db)):
    queries = await db.fetch("""
        SELECT query_id, session_id, text_query, image_query, od_json, ocr_text, asr_text, created_at
        FROM queries
        WHERE session_id = $1
        ORDER BY created_at ASC
    """, str(session))

    if not queries:
        raise HTTPException(status_code=404, detail="No history found")

    history_items = []

    for q in queries:
        results = await db.fetch("""
            SELECT qr.keyframe_id, k.video_id, k.frame_number, k.timestamp_ms, k.image_url, k.metadata,
                   qr.rank, qr.score
            FROM query_results qr
            LEFT JOIN keyframes k ON qr.keyframe_id = k.keyframe_id
            WHERE qr.query_id = $1
            ORDER BY qr.rank ASC
        """, str(q['query_id']))

        history_items.append(
            HistoryItem(
                query_id=q['query_id'],
                session_id=q['session_id'],
                text_query=q['text_query'],
                image_query=q['image_query'],
                od_json=q['od_json'],
                ocr_text=q['ocr_text'],
                asr_text=q['asr_text'],
                query_time=q['created_at'],
                results=[HistoryResult(**r) for r in results]
            )
        )

    return HistoryResponse(
        session_id=session,
        queries=history_items
    )


@router.get("/history/all")
async def get_all_history(db=Depends(database.get_db)):
    query = """
        SELECT q.query_id, q.session_id, q.text_query, q.image_query, q.od_json, q.ocr_text, q.asr_text,
               q.created_at AS query_time,
               k.keyframe_id, k.video_id, k.frame_number, k.timestamp_ms, k.image_url, k.metadata,
               qr.rank, qr.score
        FROM queries q
        LEFT JOIN query_results qr ON q.query_id = qr.query_id
        LEFT JOIN keyframes k ON qr.keyframe_id = k.keyframe_id
        ORDER BY query_time DESC, qr.rank ASC
    """

    rows = await db.fetch(query)  # ✅ fetch_all returns list of Row objects (dict-like)

    grouped: Dict[UUID, HistoryItem] = {}

    for row in rows:
        qid = row["query_id"]
        if qid not in grouped:
            grouped[qid] = HistoryItem(
                query_id=row["query_id"],
                session_id=row["session_id"],
                text_query=row["text_query"],
                image_query=row["image_query"],
                od_json=row["od_json"],
                ocr_text=row["ocr_text"],
                asr_text=row["asr_text"],
                query_time=row["query_time"],
                results=[]
            )

        if row["keyframe_id"]:
            grouped[qid].results.append(
                HistoryResult(
                    keyframe_id=row["keyframe_id"],
                    video_id=row["video_id"],
                    frame_number=row["frame_number"],
                    timestamp_ms=row["timestamp_ms"],
                    image_url=row["image_url"],
                    metadata=row["metadata"],
                    rank=row["rank"],
                    score=row["score"]
                )
            )

    return {"history": list(grouped.values())}