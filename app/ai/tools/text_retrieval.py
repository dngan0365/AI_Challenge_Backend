# tools.py
from typing import Optional, Dict, Any, List
from PIL import Image
import io, requests
import torch
from llama_index.core.tools import FunctionTool

# --- your embedding + vector search imports ---
from app.ai.model.gemma_model import get_qwen_model_cached, embed_qwen
from app.ai.model.siglip_model import get_siglip_model_cached, embed_siglip
from app.ai.vectordatabase.vectorsearch import text_vectorsearch, image_vectorsearch

def _pack_results(results) -> Dict[Any, Any]:
    """Chuẩn hoá kết quả từ LlamaIndex Retriever -> JSON nhẹ nhàng."""
    object_property: List[Dict[Any]] = []
    object_metadata: List[Any] = []
    for r in results.objects:
        object_property.append(r.properties)
        object_metadata.append(r.metadata.distance)
        # node = getattr(r, "node", None)
        # meta = getattr(node, "metadata", {}) if node else {}
        # kid = (
        #     (meta.get("keyframe_id") or meta.get("id") or getattr(node, "id_", None))
        #     if node else None
        # )
        # score = float(getattr(r, "score", 0.0)) if hasattr(r, "score") else None
        # if kid:
        #     keyframe_ids.append(kid)
        # matches.append({"id": kid, "score": score, "metadata": meta})

    return {"property": object_property, "distance": object_metadata}


def get_text_embedding(text: str):
    tokenizer, model = get_qwen_model_cached()
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        last_hidden_state = outputs.last_hidden_state  # (batch, seq_len, hidden)

        # Attention mask để bỏ padding
        mask = inputs["attention_mask"].unsqueeze(-1).expand(last_hidden_state.size())
        masked_embeddings = last_hidden_state * mask

        # Mean pooling
        sum_embeddings = masked_embeddings.sum(dim=1)
        sum_mask = mask.sum(dim=1)
        embeddings = sum_embeddings / sum_mask

        emb = embeddings[0].cpu().numpy().tolist()
    return emb


# ---------- TEXT RETRIEVAL (Qwen) ----------
def text_retrieval(query_text: str, top_k: int = 20) -> Dict[str, Any]:
    """
    Tool: text_retrieval
    Use when the user asks to search **text-only** content.
    Input:
      - query: natural language text (en/vi)
      - top_k: number of results
    Output: {"keyframe_ids": [..], "matches": [{"id": "...","score": float,"metadata": {...}}, ...]}
    """
    query_vector = get_text_embedding(query_text)
    results = text_vectorsearch(query_text, query_vector, top_k=top_k)
    return _pack_results(results)

# Wrap thành LlamaIndex tools với mô tả rõ ràng (prompt cho tool)
TEXT_RETRIEVAL_TOOL = FunctionTool.from_defaults(
    fn=text_retrieval,
    name="text_retrieval",
    description="TEXT-ONLY search on the text vector DB (Qwen embeddings). Input: query, top_k."
)