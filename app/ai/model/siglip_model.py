import torch
from transformers import AutoProcessor, AutoModel, AutoTokenizer
from PIL import Image

SIGLIP_MODEL_ID = "google/siglip-base-patch16-224"
CACHE_DIR = r"C:\Users\mt200\.cache\huggingface\hub"  # 🔹 Windows cache folder
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

_siglip_model_cache = None
_siglip_tokenizer_cache = None
_siglip_processor_cache = None

def get_siglip_model_cached(model_id: str = SIGLIP_MODEL_ID):
    global _siglip_model_cache, _siglip_tokenizer_cache, _siglip_processor_cache
    if _siglip_model_cache is None:
        print("🔹 Loading SigLIP model from cache...")
        _siglip_model_cache = AutoModel.from_pretrained(model_id, cache_dir=CACHE_DIR).to(device)
        _siglip_tokenizer_cache = AutoTokenizer.from_pretrained(model_id, cache_dir=CACHE_DIR)
        _siglip_processor_cache = AutoProcessor.from_pretrained(model_id, cache_dir=CACHE_DIR)
        _siglip_model_cache.eval()
    return _siglip_tokenizer_cache, _siglip_processor_cache, _siglip_model_cache

def embed_siglip(input_data, mode="image", model_tuple=None):
    """
    Encode text or image to embeddings
    input_data: PIL.Image for image, str for text
    mode: "image" or "text"
    """
    if model_tuple is None:
        tokenizer, processor, model = get_siglip_model_cached()
    else:
        tokenizer, processor, model = model_tuple

    if mode == "image":
        if not isinstance(input_data, Image.Image):
            raise ValueError("Expected PIL.Image for image mode")
        inputs = processor(images=input_data, return_tensors="pt").to(device)
        with torch.no_grad():
            embeds = model.get_image_features(**inputs)
    elif mode == "text":
        if not isinstance(input_data, str):
            raise ValueError("Expected str for text mode")
        inputs = tokenizer(input_data, return_tensors="pt").to(device)
        with torch.no_grad():
            embeds = model.get_text_features(**inputs)
    else:
        raise ValueError("mode must be 'image' or 'text'")

    return embeds.cpu().numpy()
