from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStoreRetriever


_DEFAULT_COLLECTION_METADATA = {"hnsw:space": "cosine"}


def build_vector_store(
    documents: list[Document],
    embeddings: Embeddings,
    persist_directory: str | None = None,
    collection_name: str = "reliablerag",
    collection_metadata: dict | None = None,
) -> Chroma:
    return Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_directory,
        collection_name=collection_name,
        collection_metadata=collection_metadata or _DEFAULT_COLLECTION_METADATA,
    )


def load_vector_store(
    embeddings: Embeddings,
    persist_directory: str,
    collection_name: str = "reliablerag",
    collection_metadata: dict | None = None,
) -> Chroma:
    return Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
        collection_name=collection_name,
        collection_metadata=collection_metadata or _DEFAULT_COLLECTION_METADATA,
    )


def get_retriever(
    vector_store: Chroma,
    top_k: int = 2,
) -> VectorStoreRetriever:
    return vector_store.as_retriever(search_kwargs={"k": top_k})
