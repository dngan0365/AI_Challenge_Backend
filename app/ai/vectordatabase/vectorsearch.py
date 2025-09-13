from llama_index.core import VectorStoreIndex
from dotenv import load_dotenv
from weaviate.classes.query import HybridFusion

import os
import weaviate
import logging
from llama_index.core import StorageContext
from llama_index.vector_stores.weaviate import WeaviateVectorStore
from weaviate.classes.query import MetadataQuery
load_dotenv()

logger = logging.getLogger(__name__)

# credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)

def _get_client(type_retrieval) -> weaviate.WeaviateClient:
    """Helper to create a WeaviateVectorStore from index and endpoint names."""
    if type_retrieval == "image":
        logger.info("Connecting to Weaviate image vector DB")
        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=os.getenv("WEAVIATE_CLIP_IMG_URL"),
            auth_credentials=weaviate.auth.AuthApiKey(os.getenv("WEAVIATE_CLIP_IMG_API_KEY")),
            skip_init_checks=True
        )
    elif type_retrieval == "text":
        logger.info("Connecting to Weaviate text vector DB")
        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=os.getenv("WEAVIATE_TEXT_URL"),
            auth_credentials=weaviate.auth.AuthApiKey(os.getenv("WEAVIATE_TEXT_API_KEY")),
            skip_init_checks=True
        )
    else:
        logger.warning(f"Unknown type_retrieval: {type_retrieval}")
        client = None
    return client


def run_vector_search_img(client, text_query, query_embedding, collection, top_k=100):
    """Generic vector search function."""
    logger.info(f"Running image vector search: text_query='{text_query}', top_k={top_k}")
    response = collection.query.hybrid(
        query=text_query,
        query_properties=["text"],
        vector=query_embedding,
        alpha=0.8,  # weight for vector similarity
        limit=top_k,
        fusion_type=HybridFusion.RELATIVE_SCORE,
        return_metadata=MetadataQuery(score=True, explain_score=True),
    )
    logger.info(f"Image vector search response: {response}")
    client.close()
    return response

def run_vector_search_text(client, text_query, query_embedding, collection, top_k=100):
    """Generic vector search function."""
    logger.info(f"Running text vector search: text_query='{text_query}', top_k={top_k}")
    response = collection.query.hybrid(
        query=text_query,
        query_properties=["text"],
        vector=query_embedding,
        alpha=0.2,  # weight for vector similarity
        limit=top_k,
        fusion_type=HybridFusion.RELATIVE_SCORE,
        return_metadata=MetadataQuery(score=True, explain_score=True),
    )
    logger.info(f"Text vector search response: {response}")
    client.close()
    return response

def text_vectorsearch(query_text, query_embedding, top_k=100):
    """Search text vector DB using Qwen embeddings."""
    type_retrieval = "text"
    logger.info(f"text_vectorsearch called with query_text='{query_text}', top_k={top_k}")
    client = _get_client(type_retrieval)
    text_collection_name = os.getenv("TEXT_COLLECTION", "TextRetrieval")
    logger.info(f"Using text collection: {text_collection_name}")
    text_collection = client.collections.use(text_collection_name)
    return run_vector_search_text(client, query_text, query_embedding, text_collection, top_k)


def image_vectorsearch(text_query, query_embedding, top_k=100):
<<<<<<< HEAD
    """Search image vector DB using SigLIP embeddings."""
=======
    """Search image vector DB using CLIP embeddings."""
>>>>>>> 626b0db1ed60ddfa1d7c58569fdc2bedf8212879
    type_retrieval = "image"
    logger.info(f"image_vectorsearch called with text_query='{text_query}', top_k={top_k}")
    client = _get_client(type_retrieval)
    image_collection_name = os.getenv("CLIP_IMG_COLLECTION", "ImageRetrieval")
    logger.info(f"Using image collection: {image_collection_name}")
    image_collection = client.collections.use(image_collection_name)
    return run_vector_search_img(client, text_query, query_embedding, image_collection, top_k)
