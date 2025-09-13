import torch
from transformers import AutoTokenizer, AutoModel
import os
import dotenv
dotenv.load_dotenv()

GEMMA_MODEL_NAME = "google/embeddinggemma-300m"
CACHE_DIR = os.getenv("CACHE_DIR", "")  # 🔹 Windows cache folder
device = torch.device("cpu")
HF_TOKEN = os.getenv("HF_TOKEN", "")

_gemma_model_cache = None
_gemma_tokenizer_cache = None

def get_gemma_model_cached(model_name: str = GEMMA_MODEL_NAME):
    global _gemma_model_cache, _gemma_tokenizer_cache
    if _gemma_model_cache is None:
        print("🔹 Loading Gemma embedding model from cache...")
        _gemma_tokenizer_cache = AutoTokenizer.from_pretrained(model_name, token=HF_TOKEN,  cache_dir=CACHE_DIR)
        _gemma_model_cache = AutoModel.from_pretrained(model_name,  token=HF_TOKEN, cache_dir=CACHE_DIR, low_cpu_mem_usage=True).to(device)
        _gemma_model_cache.eval()
    return _gemma_tokenizer_cache, _gemma_model_cache

def embed_gemma(text: str, model_tuple=None):
    """
    Encode text into vector using Gemma model.
    """
    if model_tuple is None:
        tokenizer, model = get_gemma_model_cached()
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
    tokenizer, model = get_gemma_model_cached()
    print("loaded")
    # vector = embed_gemma(text, (tokenizer, model))
    # print("Embedding vector:", vector)
    # print("Vector shape:", vector.shape)