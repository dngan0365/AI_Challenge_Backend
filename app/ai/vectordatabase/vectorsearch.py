from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.vertexaivectorsearch import VertexAIVectorStore
from google.cloud import aiplatform
from google.oauth2 import service_account

PROJECT_ID = "gen-lang-client-0974620078"
REGION = "asia-southeast1"
GCS_BUCKET_NAME = "image-retrieval"
VS_TEXT_INDEX = "text-retrieval-index"
VS_TEXT_ENDPOINT = "text-retrieval-endpoint"
VS_IMAGE_INDEX = "image-retrieval-index"
VS_IMAGE_ENDPOINT = "image-retrieval-endpoint"

CREDENTIALS_PATH = "C:/Users/mt200/OneDrive/Desktop/AI/AI_challenge/software/back-end/service-account.json"

credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)


def _get_vector_store(index_name: str, endpoint_name: str) -> VertexAIVectorStore:
    """Helper to create a VertexAIVectorStore from index and endpoint names."""
    aiplatform.init(project=PROJECT_ID, location=REGION, credentials=credentials)
    indexes = aiplatform.MatchingEngineIndex.list(filter=f'display_name="{index_name}"')
    if not indexes:
        raise ValueError(f"❌ Index {index_name} not found")

    vs_index = aiplatform.MatchingEngineIndex(index_name=indexes[0].resource_name)
    vs_endpoint = aiplatform.MatchingEngineIndexEndpoint(endpoint_name=endpoint_name)

    return VertexAIVectorStore(
        project_id=PROJECT_ID,
        region=REGION,
        index_id=vs_index.resource_name,
        endpoint_id=vs_endpoint.resource_name,
        gcs_bucket_name=GCS_BUCKET_NAME,
        credentials_path=CREDENTIALS_PATH,
    )


def run_vector_search(query_embedding, index_name: str, endpoint_name: str, top_k=50, embed_model=None):
    """Generic vector search function."""
    vector_store = _get_vector_store(index_name, endpoint_name)
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store, embed_model=embed_model)
    retriever = index.as_retriever(similarity_top_k=top_k)
    return retriever.retrieve(query_embedding)


def text_vectorsearch(query_embedding, top_k=50, embed_model=None):
    """Search text vector DB using Qwen embeddings."""
    return run_vector_search(query_embedding, VS_TEXT_INDEX, VS_TEXT_ENDPOINT, top_k, embed_model)


def image_vectorsearch(query_embedding, top_k=50, embed_model=None):
    """Search image vector DB using SigLIP embeddings."""
    return run_vector_search(query_embedding, VS_IMAGE_INDEX, VS_IMAGE_ENDPOINT, top_k, embed_model)
