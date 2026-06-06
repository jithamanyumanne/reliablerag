# Setup Guide

Choose the guide for your environment:

- [Local (PyCharm / VSCode)](docs/local.md) — full dev setup with Ollama
- [Google Colab](docs/colab.md) — cloud compute with HuggingFace models
- [Kaggle](docs/kaggle.md) — cloud compute with HuggingFace models

---

## Adding a new provider

To add support for a new LLM provider (e.g. OpenAI):

1. Add an entry to `_PROVIDERS` in `src/reliablerag/providers.py`:
```python
"openai": {
    "embeddings": ("langchain_openai", "OpenAIEmbeddings"),
    "llm":        ("langchain_openai", "ChatOpenAI"),
},
```
2. Add the package to `dependencies` in `pyproject.toml`:
```toml
"langchain-openai>=0.1.0",
```
3. Set `PROVIDER=openai` in your environment and update `EMBEDDING_MODEL` / `LLM_MODEL` to match the provider's format.
4. Run `uv sync` to install.