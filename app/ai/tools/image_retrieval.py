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


# ---------- IMAGE RETRIEVAL (SigLIP) ----------
def image_retrieval(
    text: Optional[str] = None,
    image_url: Optional[str] = None,
    top_k: int = 50
) -> Dict[str, Any]:
    """
    Tool: image_retrieval
    Use when the user asks to find **keyframes/images** similar to:
      - a text description (set `text`)
      - or a reference image URL (set `image_url`)
    Exactly one of `text` or `image_url` must be provided.
    Output: {"keyframe_ids": [..], "matches": [{"id": "...","score": float,"metadata": {...}}, ...]}
    """
    tokenizer, processor, model = get_siglip_model_cached()

    if (text is None) == (image_url is None):
        raise ValueError("Provide exactly one of `text` or `image_url`.")

    if text is not None:
        emb = embed_siglip(text, mode="text", model_tuple=(tokenizer, processor, model))
    else:
        resp = requests.get(image_url, timeout=20)
        img = Image.open(io.BytesIO(resp.content)).convert("RGB")
        emb = embed_siglip(img, mode="image", model_tuple=(tokenizer, processor, model))

    results = image_vectorsearch(emb, top_k=top_k)
    return _pack_results(results)


IMAGE_RETRIEVAL_TOOL = FunctionTool.from_defaults(
    fn=image_retrieval,
    name="image_retrieval",
    description="IMAGE search on the image vector DB (SigLIP). Input: text or image_url (exactly one), top_k."
)