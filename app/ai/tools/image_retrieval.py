# tools.py
from typing import Optional, Dict, Any, List
from PIL import Image
import io, requests
import torch
from llama_index.core.tools import FunctionTool
import numpy as np
# --- your embedding + vector search imports ---
from app.ai.model.qwen_model import get_qwen_model_cached, embed_qwen
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


# ---------- IMAGE RETRIEVAL (SigLIP) ----------

# --- 2. Hàm tạo embedding từ text ---
def embed_text(text: str) -> np.ndarray:
    """
    Tạo embedding vector cho một câu text sử dụng SigLIP
    """
    tokenizer, processor, model = get_siglip_model_cached()
    # device = "cuda" if torch.cuda.is_available() else "cpu"
    # model.to("cpu")
    # model.eval()
    inputs = processor(text=[text], return_tensors="pt", padding=True)
    inputs = {k: v.to("cpu") for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = model.get_text_features(**inputs)
    
    vector = outputs.cpu().numpy()
    vector = vector / np.linalg.norm(vector, axis=-1, keepdims=True)  # normalize
    return vector[0]


def image_retrieval(
    text_query: Optional[str] = None,
    image_query: Optional[str] = None,
    top_k: int = 20
) -> Dict[str, Any]:
    """
    Tool: image_retrieval
    Use when the user asks to find **keyframes/images** similar to:
      - a text description (set `text`)
    Output: {"keyframe_ids": [..], "matches": [{"id": "...","score": float,"metadata": {...}}, ...]}
    """
    query_embedding = embed_text(image_query)

    # if (text is None) == (image_url is None):
    #     raise ValueError("Provide exactly one of `text` or `image_url`.")

    # if text is not None:
    # emb = embed_siglip(text, mode="text", model_tuple=(tokenizer, processor, model))
    # else:
    #     resp = requests.get(image_url, timeout=20)
    #     img = Image.open(io.BytesIO(resp.content)).convert("RGB")
    #     emb = embed_siglip(img, mode="image", model_tuple=(tokenizer, processor, model))

    results = image_vectorsearch(text_query, query_embedding, top_k=top_k)
    return _pack_results(results)


IMAGE_RETRIEVAL_TOOL = FunctionTool.from_defaults(
    fn=image_retrieval,
    name="image_retrieval",
    description="IMAGE search on the image vector DB (SigLIP). Input: text or image_url (exactly one), top_k."
)