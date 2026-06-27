# Kaggle Setup

## 1. Open the notebook

Import from GitHub: `File → Import Notebook → GitHub`, paste the repo URL and select `02_cuad_rag.ipynb`.

Or upload the `.ipynb` file manually.

---

## 2. Set secrets

Go to `Add-ons → Secrets` and add all of the following:

| Secret | Value |
|---|---|
| `PROVIDER` | `ollama` |
| `EMBEDDING_MODEL` | `nomic-embed-text-v2-moe:latest` |
| `GENERATOR_MODEL` | `llama3.1:8b-instruct-q4_K_M` |
| `JUDGE_MODEL` | `llama3.1:8b-instruct-q4_K_M` |
| `CHROMA_PERSIST_DIR` | `/kaggle/working/data/chroma_db` |
| `HF_TOKEN` | your HuggingFace token (required to download the ragbench dataset) |

---

## 3. Enable GPU accelerator

In the right sidebar under `Session options`, set `Accelerator` to **GPU T4 x2** for best performance.

---

## 4. Run the notebook

The first cell automatically:
1. Installs the `reliablerag` package from GitHub
2. Installs Ollama and starts the background daemon
3. Pulls the required models (~6 GB total — takes 5–10 min on first run, cached on subsequent runs)

Run all cells after that. Total runtime for 20 CUAD samples with 3 judge runs is roughly 60–90 min on a T4.