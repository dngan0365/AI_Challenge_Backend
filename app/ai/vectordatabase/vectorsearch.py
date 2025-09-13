from llama_index.core import VectorStoreIndex
from dotenv import load_dotenv
import os
import weaviate
from llama_index.core import StorageContext
from llama_index.vector_stores.weaviate import WeaviateVectorStore
from weaviate.classes.query import MetadataQuery
load_dotenv()

# credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)

def _get_client(type_retrieval) -> weaviate.WeaviateClient:
    """Helper to create a WeaviateVectorStore from index and endpoint names."""
    if type_retrieval == "image":
        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=os.getenv("WEAVIATE_IMG_URL"),
            auth_credentials=weaviate.auth.AuthApiKey(os.getenv("WEAVIATE_IMG_API_KEY")),
            skip_init_checks=True
        )
    if type_retrieval == "text":
        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=os.getenv("WEAVIATE_TEXT_URL"),
            auth_credentials=weaviate.auth.AuthApiKey(os.getenv("WEAVIATE_TEXT_API_KEY")),
            skip_init_checks=True
        )
    
    return client


def run_vector_search_img(client, text_query, query_embedding, collection, top_k=100):
    """Generic vector search function."""
    response = collection.query.hybrid(
    query=text_query,
    vector=query_embedding,
    alpha=0.3,
    limit=top_k,
    return_metadata=MetadataQuery(distance=True)
)
    client.close()
    return response

def run_vector_search_text(client, text_query, query_embedding, collection, top_k=100):
    """Generic vector search function."""
    response = collection.query.hybrid(
    query=text_query,
    query_properties=["text", "title"],
    vector=query_embedding,
    alpha=0.3,
    limit=top_k,
    return_metadata=MetadataQuery(distance=True)
)
    client.close()
    return response

def text_vectorsearch(query_text, query_embedding, top_k=100):
    """Search text vector DB using Qwen embeddings."""
    type_retrieval = "text"
    client = _get_client(type_retrieval)
    text_collection = client.collections.use(os.getenv("TEXT_COLLECTION", "TextRetrieval"))
    return run_vector_search_text(client, query_text, query_embedding, text_collection, top_k)


def image_vectorsearch(text_query, query_embedding, top_k=100):
    """Search image vector DB using SigLIP embeddings."""
    type_retrieval = "image"
    client = _get_client(type_retrieval)
    image_collection = client.collections.use(os.getenv("IMG_COLLECTION", "ImageRetrieval"))
    return run_vector_search_img(client, text_query, query_embedding, image_collection, top_k)
