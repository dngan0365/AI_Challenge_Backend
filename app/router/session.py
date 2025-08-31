from fastapi import APIRouter, Depends
from app.db import database
from app.models.session import SessionResponse, AllSessionsResponse
import asyncpg

router = APIRouter()

@router.post("/session", response_model=SessionResponse)
async def create_session(db=Depends(database.get_db)):
    query = "INSERT INTO sessions DEFAULT VALUES RETURNING session_id, created_at"
    result = await db.fetchrow(query)
    return SessionResponse(session_id=result['session_id'], created_at=result['created_at'])

@router.get("/sessions", response_model=list[AllSessionsResponse])
async def get_all_sessions(db=Depends(database.get_db)):
    rows = await db.fetch("SELECT session_id, created_at, last_updated FROM sessions ORDER BY created_at DESC")
    return [AllSessionsResponse(**row) for row in rows]