"""
Embeddings  : HuggingFace sentence-transformers  (free, local, no API key)
Vector Store: ChromaDB                           (free, local, no server needed)
"""
from langchain_huggingface import HuggingFaceEmbeddings 
import chromadb
from langchain_chroma import Chroma
from core.config import config
from utils.logger import get_logger

logger = get_logger(__name__)

_embeddings = None

def get_embeddings() -> HuggingFaceEmbeddings:
    global _embeddings
    if _embeddings is None:
        logger.info(f"Loading embedding model: {config.EMBED_MODEL}")
        _embeddings = HuggingFaceEmbeddings(
            model_name=config.EMBED_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embeddings

def build_vector_store(chunks: list) -> Chroma:
    """Create and persist a new Chroma vector store from document chunks."""
    logger.info(f"Building Chroma vector store with {len(chunks)} chunks...")
    store = Chroma.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        persist_directory=config.CHROMA_PERSIST_DIR,
        collection_name=config.COLLECTION_NAME,
    )
    logger.info(f"Vector store saved to {config.CHROMA_PERSIST_DIR}")
    return store

def load_vector_store() -> Chroma:
    """Load existing persisted Chroma vector store."""
    logger.info(f"Loading vector store from {config.CHROMA_PERSIST_DIR}")
    return Chroma(
        persist_directory=config.CHROMA_PERSIST_DIR,
        embedding_function=get_embeddings(),
        collection_name=config.COLLECTION_NAME,
    )
