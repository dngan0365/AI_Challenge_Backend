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


def get_search_results(query_data: QueryRequest, query_type="both"):
    """Run image/text retrieval and return combined results."""
    text_query = query_data.text_query
    image_query = query_data.image_query

    logger.info(
        f"get_search_results called with text_query='{text_query}', "
        f"image_query='{image_query}', query_type='{query_type}'"
    )

    def safe_get_list(d, key):
        v = d.get(key, [])
        return v if isinstance(v, list) else []

    # Run retrievals
    result_1 = image_retrieval(image_query=image_query) if query_type in ["image", "both"] and image_query else {"property": [], "distance": []}
    result_2 = text_retrieval(query_text=text_query) if query_type in ["text", "both"] and text_query else {"property": [], "distance": []}

    prop1 = safe_get_list(result_1, "property")
    dist1 = safe_get_list(result_1, "distance")
    prop2 = safe_get_list(result_2, "property")
    dist2 = safe_get_list(result_2, "distance")

    # Pad distances if needed
    if len(dist1) < len(prop1):
        dist1 += [None] * (len(prop1) - len(dist1))
    if len(dist2) < len(prop2):
        dist2 += [None] * (len(prop2) - len(dist2))

    results = []

    def extract_frame_id(prop):
        if isinstance(prop, dict):
            for k in ["frame_id", "id", "keyframe_id"]:
                if k in prop:
                    return prop[k]
        elif isinstance(prop, (list, tuple)) and prop:
            return prop[0]
        return None

    for prop, dist in zip(prop1, dist1):
        frame_id = extract_frame_id(prop)
        results.append({"frame_id": frame_id, "property": prop, "distance": dist, "source": "image"})
    for prop, dist in zip(prop2, dist2):
        frame_id = extract_frame_id(prop)
        results.append({"frame_id": frame_id, "property": prop, "distance": dist, "source": "text"})

    # Deduplicate
    unique_results = {}
    for r in results:
        if r["frame_id"] not in unique_results:
            unique_results[r["frame_id"]] = r

    return list(unique_results.values())


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
