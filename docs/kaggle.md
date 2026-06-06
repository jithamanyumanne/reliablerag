# Kaggle Setup

## 1. Open the notebook

Import from GitHub under `File → Import Notebook → GitHub` and paste the repo URL, or upload the `.ipynb` file manually.

---

## 2. Set secrets

Go to **Add-ons → Secrets** and add:

| Secret | Example value |
|---|---|
| `PROVIDER` | `huggingface` |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` |
| `LLM_MODEL` | `HuggingFaceH4/zephyr-7b-beta` |
| `CHROMA_PERSIST_DIR` | `/kaggle/working/data/chroma_db` |

---

## 3. Run the notebook

The first cell installs the `reliablerag` package automatically from GitHub. Run all cells.
