from fastapi import APIRouter, Depends, Query, HTTPException
from uuid import UUID
from app.db import database
from app.models.query import QueryRequest, QueryResponse
from llama_index.core.llms import ChatMessage
import logging
import json
# 🔥 Import your agent
from app.ai.agents.main import agent, ctx 

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/query", response_model=QueryResponse)
async def create_query(
    query_data: QueryRequest,
    session: UUID = Query(..., description="Session ID"),
    db=Depends(database.get_db)
):
    """Create a new query and perform search using the agent."""
    try:
        async with db.transaction():
            # 1. Insert query record
            insert_query = """
            INSERT INTO queries (session_id, text_query, image_query, od_json, ocr_text, asr_text)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING query_id
            """
            query_result = await db.fetchrow(
                insert_query,
                session,
                query_data.text_query,
                query_data.image_query,
                query_data.od_json,
                query_data.ocr_text,
                query_data.asr_text
            )
            query_id = query_result["query_id"]

            # 2. Log user message
            user_content = []
            if query_data.text_query: user_content.append(f"Text: {query_data.text_query}")
            if query_data.image_query: user_content.append(f"Image: {query_data.image_query}")
            if query_data.ocr_text: user_content.append(f"OCR: {query_data.ocr_text}")
            if query_data.asr_text: user_content.append(f"ASR: {query_data.asr_text}")

            if user_content:
                await db.execute(
                    "INSERT INTO messages (session_id, query_id, role, content) VALUES ($1, $2, 'user', $3)",
                    session, query_id, " | ".join(user_content)
                )

            # 3. 🔥 Call agent with unified query
            user_prompt = {
                "text": query_data.text_query,
                "image": query_data.image_query,
                "ocr": query_data.ocr_text,
                "asr": query_data.asr_text
            }
            user_prompt = {k: v for k, v in user_prompt.items() if v}

            agent_response = await agent.run(
                ChatMessage(role="user", content="Find keyframes about cats")
            )
            
            logging.info(f"Agent response: {agent_response}")
            # agent returns JSON: {"reasoning": [...], "keyframe_ids": [...], "matches": [...]}
            agent_data = json.loads(agent_response.response)


            # 4. Save agent results in DB
            search_results = []
            for rank, m in enumerate(agent_data.get("matches", []), start=1):
                await db.execute(
                    "INSERT INTO query_results (query_id, keyframe_id, rank, score) VALUES ($1, $2, $3, $4)",
                    query_id, m["id"], rank, m.get("score")
                )
                search_results.append({
                    "keyframe_id": m["id"],
                    "metadata": m.get("metadata"),
                    "score": m.get("score"),
                    "rank": rank
                })

            # 5. Log agent summary
            await db.execute(
                "INSERT INTO messages (session_id, query_id, role, content) VALUES ($1, $2, 'agent', $3)",
                session, query_id, f"Reasoning: {agent_data.get('reasoning', [])}"
            )

            # 6. Return API response
            return QueryResponse(
                query_id=query_id,
                session_id=session,
                results=search_results
            )

    except Exception as e:
        logger.error(f"Error creating query: {e}")
        raise HTTPException(status_code=500, detail="Failed to create query")
