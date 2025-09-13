from fastapi import APIRouter, Depends, Query, HTTPException
from uuid import UUID
from app.db import database
from app.models.query import QueryRequest
import logging

# 🔥 Import your agent
from app.ai.tools.image_retrieval import image_retrieval
from app.ai.tools.text_retrieval import text_retrieval

router = APIRouter()
logger = logging.getLogger(__name__)

def safe_get_list(d, key):
    v = d.get(key, [])
    return v if isinstance(v, list) else []

def safe_get_score_list(d):
    """Extract scores from retrieval results (already packed by _pack_results)."""
    scores = d.get("score", [])
    props = d.get("property", [])

    # đảm bảo scores là list
    if not isinstance(scores, list):
        scores = [scores]

    # pad nếu thiếu
    while len(scores) < len(props):
        scores.append(None)

    return scores

def get_search_results(query_data: QueryRequest, query_type="both"):
    text_query = query_data.text_query
    image_query = query_data.image_query

    result_1 = image_retrieval(image_query=image_query) if query_type in ["image", "both"] and image_query else {"property": [], "score": []}
    result_2 = text_retrieval(query_text=text_query) if query_type in ["text", "both"] and text_query else {"property": [], "score": []}

    prop1 = result_1.get("property", [])
    dist1 = safe_get_score_list(result_1)

    prop2 = result_2.get("property", [])
    dist2 = safe_get_score_list(result_2)

    results = []

    def extract_frame_id(prop):
        if isinstance(prop, dict):
            for k in ["frame_id", "id", "keyframe_id"]:
                if k in prop:
                    return prop[k]
        elif isinstance(prop, (list, tuple)) and prop:
            return prop[0]
        return None

    # gom image
    for prop, dist in zip(prop1, dist1):
        frame_id = extract_frame_id(prop)
        results.append({"frame_id": frame_id, "property": prop, "score": dist, "source": "image"})

    # gom text
    for prop, dist in zip(prop2, dist2):
        frame_id = extract_frame_id(prop)
        results.append({"frame_id": frame_id, "property": prop, "score": dist, "source": "text"})

    # merge
    unique_results = {}
    for r in results:
        fid = r["frame_id"]
        if fid not in unique_results:
            unique_results[fid] = {
                "frame_id": fid,
                "property": r["property"],
                "image_score": 0.0,
                "text_score": 0.0,
                "total_score": 0.0
            }
        if r["source"] == "image":
            unique_results[fid]["image_score"] = r["score"] or 0.0
        elif r["source"] == "text":
            unique_results[fid]["text_score"] = r["score"] or 0.0

        if not unique_results[fid]["property"]:
            unique_results[fid]["property"] = r["property"]

    # compute + sort
    for r in unique_results.values():
        r["total_score"] = (r["image_score"] or 0.0) + (r["text_score"] or 0.0)

    return sorted(unique_results.values(), key=lambda x: x["total_score"], reverse=True)

async def insert_query_and_log(db, session: UUID, query_data: QueryRequest):
    """Insert query and log user messages safely, return query_id."""
    insert_query = """
    INSERT INTO queries (session_id, text_query, image_query)
    VALUES ($1, $2, $3)
    RETURNING query_id
    """
    query_id = await db.fetchval(
        insert_query,
        session,
        query_data.text_query,
        query_data.image_query,
    )

    # Log user message if present
    user_content = []
    if query_data.text_query:
        user_content.append(f"Text: {query_data.text_query}")
    if query_data.image_query:
        user_content.append(f"Image: {query_data.image_query}")

    if user_content:
        await db.execute(
            "INSERT INTO messages (session_id, query_id, role, content) VALUES ($1, $2, 'user', $3)",
            session,
            query_id,
            " | ".join(user_content),
        )

    return query_id


@router.post("/query-img")
async def create_query_img(
    query_data: QueryRequest,
    session: UUID = Query(..., description="Session ID"),
    db=Depends(database.get_db),
):
    """Create a new query and perform search using text+image."""
    try:
        async with db.transaction():
            query_id = await insert_query_and_log(db, session, query_data)
            search_results = get_search_results(query_data, query_type="both")

            return {"query_id": query_id, "session_id": session, "results": search_results}
    except Exception as e:
        logger.exception(f"Error in /query-img: {e}")
        raise HTTPException(status_code=500, detail="Failed to create query")


@router.post("/query-text")
async def create_query_text(
    query_data: QueryRequest,
    session: UUID = Query(..., description="Session ID"),
    db=Depends(database.get_db),
):
    """Create a new query and perform search using text only."""
    try:
        async with db.transaction():
            query_id = await insert_query_and_log(db, session, query_data)
            search_results = get_search_results(query_data, query_type="both")

            return {"query_id": query_id, "session_id": session, "results": search_results}
    except Exception as e:
        logger.exception(f"Error in /query-text: {e}")
        raise HTTPException(status_code=500, detail="Failed to create query")
