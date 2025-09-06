import torch
from transformers import AutoTokenizer, AutoModel
import os
import dotenv
dotenv.load_dotenv()

QWEN_MODEL_NAME = "google/embeddinggemma-300m"
CACHE_DIR = os.getenv("CACHE_DIR", "")  # 🔹 Windows cache folder
device = torch.device("cpu")

_qwen_model_cache = None
_qwen_tokenizer_cache = None

def get_qwen_model_cached(model_name: str = QWEN_MODEL_NAME):
    global _qwen_model_cache, _qwen_tokenizer_cache
    if _qwen_model_cache is None:
        print("🔹 Loading Qwen embedding model from cache...")
        _qwen_tokenizer_cache = AutoTokenizer.from_pretrained(model_name, cache_dir=CACHE_DIR)
        _qwen_model_cache = AutoModel.from_pretrained(model_name, cache_dir=CACHE_DIR, low_cpu_mem_usage=True).to(device)
        _qwen_model_cache.eval()
    return _qwen_tokenizer_cache, _qwen_model_cache

def embed_qwen(text: str, model_tuple=None):
    """
    Encode text into vector using Qwen model.
    """
    if model_tuple is None:
        tokenizer, model = get_qwen_model_cached()
    else:
        tokenizer, model = model_tuple

    inputs = tokenizer(text, return_tensors="pt", truncation=True).to(device)
    with torch.no_grad():
        outputs = model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1)
    return embeddings.cpu().numpy()

if __name__ == "__main__":
    # Test the embedding function
    # text = "Hello, this is a test sentence."
    tokenizer, model = get_qwen_model_cached()
    print("loaded")
    # vector = embed_qwen(text, (tokenizer, model))
    # print("Embedding vector:", vector)
    # print("Vector shape:", vector.shape)