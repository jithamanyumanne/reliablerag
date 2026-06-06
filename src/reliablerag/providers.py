import importlib

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel

_PROVIDERS: dict[str, dict[str, tuple[str, str]]] = {
    "ollama": {
        "embeddings": ("langchain_ollama", "OllamaEmbeddings"),
        "llm":        ("langchain_ollama", "ChatOllama"),
    },
    # "huggingface": {
    #     "embeddings": ("langchain_huggingface", "HuggingFaceEmbeddings"),
    #     "llm":        ("langchain_huggingface", "ChatHuggingFace"),
    # },
}


def _resolve(provider: str, kind: str):
    if provider not in _PROVIDERS:
        raise ValueError(f"Unsupported provider: {provider!r}. Supported: {list(_PROVIDERS)}")
    module_name, class_name = _PROVIDERS[provider][kind]
    module = importlib.import_module(module_name)
    return getattr(module, class_name)


def create_embeddings(provider: str, model: str, **kwargs) -> Embeddings:
    return _resolve(provider, "embeddings")(model=model, **kwargs)


def create_llm(provider: str, model: str, **kwargs) -> BaseChatModel:
    return _resolve(provider, "llm")(model=model, **kwargs)