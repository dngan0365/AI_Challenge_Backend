# main_agent.py
from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.workflow import Context
from llama_index.llms.openai import OpenAI as LlamaOpenAI  # ⚠️ dùng LlamaIndex LLM wrapper
# Không dùng: from openai import OpenAI

from app.ai.tools.image_retrieval import IMAGE_RETRIEVAL_TOOL
from app.ai.tools.text_retrieval import TEXT_RETRIEVAL_TOOL

SYSTEM_PROMPT = """
You are a Retrieval Orchestrator for keyframe search.
You have two tools:
- text_retrieval(query, top_k): for TEXT-ONLY search on the text vector DB (Qwen embeddings).
- image_retrieval(text=None, image_url=None, top_k): for IMAGE search on the image vector DB (SigLIP). Exactly one of text or image_url must be set.

Decision rules:
- If the user gives an image URL or asks for similar images/keyframes visually → use image_retrieval.
- If the user gives only text and wants similar text/keyframes → use both text_retrieval and image_retrieval, normalize scores, and combine results.

Output format (MANDATORY):
Return ONLY a compact JSON with keys:
{
  "reasoning": ["short step 1", "short step 2", ...],
  "keyframe_ids": ["<id1>", "<id2>", ...],
  "matches": [{"id":"<id>", "score": <float or null>, "metadata": {...}}, ...]
}
The `keyframe_ids` list MUST be sorted by descending relevance.
Do NOT include extra commentary outside JSON.
"""

llm = LlamaOpenAI(model="gpt-4o-mini", temperature=0)  # hoặc model bạn muốn

query_engine_tools = [TEXT_RETRIEVAL_TOOL, IMAGE_RETRIEVAL_TOOL]

agent = ReActAgent(
    tools=query_engine_tools,
    llm=llm,
    system_prompt=SYSTEM_PROMPT,
    verbose=True,                 # bật log reasoning trong console
    allow_parallel_tool_calls=False
)

# Context để giữ state cho phiên
ctx = Context(agent)

