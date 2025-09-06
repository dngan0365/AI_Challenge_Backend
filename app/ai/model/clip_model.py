import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
from dotenv import load_dotenv
import os

load_dotenv()

CLIP_MODEL_ID = "openai/clip-vit-base-patch32"
CACHE_DIR = os.getenv("CACHE_DIR", "")  # folder cache
device = torch.device("cpu")  # or "cuda" nếu bạn có GPU

_clip_model_cache = None
_clip_processor_cache = None

def get_clip_model_cached(model_id: str = CLIP_MODEL_ID):
    global _clip_model_cache, _clip_processor_cache
    if _clip_model_cache is None:
        print("🔹 Loading CLIP model from cache...")
        _clip_model_cache = CLIPModel.from_pretrained(model_id, cache_dir=CACHE_DIR).to(device)
        _clip_processor_cache = CLIPProcessor.from_pretrained(model_id, cache_dir=CACHE_DIR)
        _clip_model_cache.eval()
    return _clip_processor_cache, _clip_model_cache

def embed_clip(input_data, mode="image", model_tuple=None):
    """
    Encode text or image to embeddings using CLIP.
    input_data: PIL.Image for image, str for text
    mode: "image" or "text"
    """
    if model_tuple is None:
        processor, model = get_clip_model_cached()
    else:
        processor, model = model_tuple

    if mode == "image":
        if not isinstance(input_data, Image.Image):
            raise ValueError("Expected PIL.Image for image mode")
        inputs = processor(images=input_data, return_tensors="pt").to(device)
        with torch.no_grad():
            embeds = model.get_image_features(**inputs)
    elif mode == "text":
        if not isinstance(input_data, str):
            raise ValueError("Expected str for text mode")
        inputs = processor(text=input_data, return_tensors="pt").to(device)
        with torch.no_grad():
            embeds = model.get_text_features(**inputs)
    else:
        raise ValueError("mode must be 'image' or 'text'")

    return embeds.cpu().numpy()
