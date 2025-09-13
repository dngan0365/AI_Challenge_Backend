# main_agent.py
from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.workflow import Context
from llama_index.llms.openai import OpenAI as LlamaOpenAI  # ⚠️ dùng LlamaIndex LLM wrapper
# Không dùng: from openai import OpenAI

from app.ai.tools.image_retrieval import IMAGE_RETRIEVAL_TOOL
# from app.ai.tools.text_retrieval import TEXT_RETRIEVAL_TOOL

SYSTEM_PROMPT = """
You are a Retrieval Orchestrator for keyframe search.
Use tool IMAGE_RETRIEVAL_TOOL to search on the image based on text.

Do NOT include extra commentary outside JSON.
"""

llm = LlamaOpenAI(model="gpt-4o-mini", temperature=0.1)  # hoặc model bạn muốn

query_engine_tools = [IMAGE_RETRIEVAL_TOOL]

agent = ReActAgent(
    tools=query_engine_tools,
    llm=llm,
    system_prompt=SYSTEM_PROMPT,
    verbose=True,                 # bật log reasoning trong console
    allow_parallel_tool_calls=False
)

# Context để giữ state cho phiên
ctx = Context(agent)

