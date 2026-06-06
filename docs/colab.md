# Google Colab Setup

## 1. Open the notebook

Open directly from GitHub:
```
https://colab.research.google.com/github/saikrishna1729/reliablerag/blob/main/notebooks/01_basic_rag.ipynb
```

Or upload the `.ipynb` file manually via `File → Upload notebook`.

---

## 2. Set secrets

Go to the 🔑 **Secrets** panel in the left sidebar and add:

| Secret | Example value |
|---|---|
| `PROVIDER` | `huggingface` |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` |
| `LLM_MODEL` | `HuggingFaceH4/zephyr-7b-beta` |
| `CHROMA_PERSIST_DIR` | `/content/data/chroma_db` |

---

## 3. Run the notebook

The first cell installs the `reliablerag` package automatically from GitHub. Run all cells.

---

## Saving changes back to GitHub

`File → Save a copy in GitHub` — commits the notebook directly to the repo without copy-pasting.
