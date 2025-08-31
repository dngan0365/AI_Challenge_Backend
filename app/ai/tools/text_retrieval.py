# tools.py
from typing import Optional, Dict, Any, List
from PIL import Image
import io, requests

from llama_index.core.tools import FunctionTool

# --- your embedding + vector search imports ---
from app.ai.model.qwen_model import get_qwen_model_cached, embed_qwen
from app.ai.model.siglip_model import get_siglip_model_cached, embed_siglip
from app.ai.vectordatabase.vectorsearch import text_vectorsearch, image_vectorsearch

def _pack_results(results) -> Dict[str, Any]:
    """Chuẩn hoá kết quả từ LlamaIndex Retriever -> JSON nhẹ nhàng."""
    keyframe_ids: List[str] = []
    matches: List[Dict[str, Any]] = []
    for r in results:
        node = getattr(r, "node", None)
        meta = getattr(node, "metadata", {}) if node else {}
        kid = (
            (meta.get("keyframe_id") or meta.get("id") or getattr(node, "id_", None))
            if node else None
        )
        score = float(getattr(r, "score", 0.0)) if hasattr(r, "score") else None
        if kid:
            keyframe_ids.append(kid)
        matches.append({"id": kid, "score": score, "metadata": meta})
    return {"keyframe_ids": keyframe_ids, "matches": matches}

# ---------- TEXT RETRIEVAL (Qwen) ----------
def text_retrieval(query: str, top_k: int = 50) -> Dict[str, Any]:
    """
    Tool: text_retrieval
    Use when the user asks to search **text-only** content.
    Input:
      - query: natural language text (en/vi)
      - top_k: number of results
    Output: {"keyframe_ids": [..], "matches": [{"id": "...","score": float,"metadata": {...}}, ...]}
    """
    tok, mdl = get_qwen_model_cached()
    emb = embed_qwen(query, (tok, mdl))
    results = text_vectorsearch(emb, top_k=top_k)
    return _pack_results(results)

# Wrap thành LlamaIndex tools với mô tả rõ ràng (prompt cho tool)
TEXT_RETRIEVAL_TOOL = FunctionTool.from_defaults(
    fn=text_retrieval,
    name="text_retrieval",
    description="TEXT-ONLY search on the text vector DB (Qwen embeddings). Input: query, top_k."
)