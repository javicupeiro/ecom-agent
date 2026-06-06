from ecom_agent.config import get_settings
from ecom_agent.rag.index import KnowledgeBase

s = get_settings()
kb = KnowledgeBase(
    s.rag.persist_dir, s.rag.collection, s.openai_api_key,
    s.rag.embedding_model, s.rag.top_k,
)
print("indexed chunks:", kb.ingest(s.rag.kb_root))