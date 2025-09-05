from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.vertexaivectorsearch import VertexAIVectorStore
from google.cloud import aiplatform
from google.oauth2 import service_account
from dotenv import load_dotenv
import os
import weaviate
from llama_index.core import StorageContext
from llama_index.vector_stores.weaviate import WeaviateVectorStore
load_dotenv()

GCS_BUCKET_NAME =  os.getenv("GCS_BUCKET_NAME", "")
REGION = os.getenv("REGION", "asia-southeast1")
PROJECT_ID = os.getenv("PROJECT_ID", "")
VS_TEXT_INDEX = os.getenv("VS_TEXT_INDEX", "")
VS_TEXT_ENDPOINT = os.getenv("VS_TEXT_ENDPOINT", "")
VS_IMAGE_INDEX = os.getenv("VS_IMAGE_INDEX", "")
VS_IMAGE_ENDPOINT = os.getenv("VS_IMAGE_ENDPOINT", "")
CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)


def _get_vector_store(index_name: str) -> WeaviateVectorStore:
    """Helper to create a WeaviateVectorStore from index and endpoint names."""
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=os.getenv("WEAVIATE_URL"),
        auth_credentials=weaviate.auth.AuthApiKey(os.getenv("WEAVIATE_API_KEY")),
    )
    vector_store = WeaviateVectorStore(weaviate_client=client, index_name=index_name)
    return vector_store


def run_vector_search(query, index_name: str, top_k=50, embed_model=None):
    """Generic vector search function."""
    vector_store = _get_vector_store(index_name)
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store, embed_model=embed_model)
    retriever = index.as_retriever(similarity_top_k=top_k)
    return retriever.retrieve(query)


def text_vectorsearch(query, top_k=50, embed_model=None):
    """Search text vector DB using Qwen embeddings."""
    return run_vector_search(query, VS_TEXT_INDEX, top_k, embed_model)


def image_vectorsearch(query, top_k=50, embed_model=None):
    """Search image vector DB using SigLIP embeddings."""
    return run_vector_search(query, VS_IMAGE_INDEX, top_k, embed_model)
