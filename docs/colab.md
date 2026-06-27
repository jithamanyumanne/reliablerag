# Google Colab Setup

> **Requires a GPU runtime.** Go to `Runtime → Change runtime type → T4 GPU` before running any cells.

---

## 1. Open the notebook

Open directly from GitHub:
```
https://colab.research.google.com/github/saikrishna1729/reliablerag/blob/main/notebooks/02_cuad_rag.ipynb
```

Or upload the `.ipynb` file manually via `File → Upload notebook`.

---

## 2. Set secrets

Go to the 🔑 **Secrets** panel in the left sidebar and add all of the following. Enable **"Notebook access"** for each one.

| Secret | Value |
|---|---|
| `PROVIDER` | `ollama` |
| `EMBEDDING_MODEL` | `nomic-embed-text-v2-moe:latest` |
| `GENERATOR_MODEL` | `llama3.1:8b-instruct-q4_K_M` |
| `JUDGE_MODEL` | `llama3.1:8b-instruct-q4_K_M` |
| `CHROMA_PERSIST_DIR` | `/content/data/chroma_db` |
| `HF_TOKEN` | your HuggingFace token (required to download the ragbench dataset) |

---

## 3. Run the notebook

The first cell automatically:
1. Installs the `reliablerag` package from GitHub
2. Installs Ollama and starts the background daemon
3. Pulls the required models (~6 GB total — takes 5–10 min on first run, cached on subsequent runs)

Run all cells after that. Total runtime for 20 CUAD samples with 3 judge runs is roughly 60–90 min on a T4.

---

## Saving changes back to GitHub

`File → Save a copy in GitHub` — commits the notebook directly to the repo without copy-pasting.