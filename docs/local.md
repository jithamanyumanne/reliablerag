# Local Setup (PyCharm / VSCode)

## Prerequisites

### 1. Python 3.13+

**macOS:**
```bash
brew install pyenv
pyenv install 3.13
pyenv local 3.13
```

**Windows:**
```powershell
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
pyenv install 3.13
pyenv local 3.13
```

Verify:
```bash
python --version
```

### 2. uv

**macOS:**
```bash
brew install uv
```

**Windows:**
```powershell
winget install astral-sh.uv
```

### 3. Ollama

**macOS:**
```bash
brew install ollama
```

**Windows:** Download the installer from [ollama.com](https://ollama.com/download/windows).

Start the daemon:
```bash
ollama serve
```

Pull the required models:
```bash
ollama pull nomic-embed-text-v2-moe:latest
ollama pull gemma4:12b-it-q4_K_M
ollama pull llama3.1:8b-instruct-q4_K_M
```

---

## Install dependencies

```bash
uv sync
```

This creates a `.venv` in the project root and installs all dependencies.

---

## Environment configuration

```bash
cp .env.example .env
```

Edit `.env` with your values:

| Variable | Description |
|---|---|
| `PROVIDER` | Provider to use. Currently supported: `ollama` |
| `EMBEDDING_MODEL` | Embedding model name |
| `GENERATOR_MODEL` | LLM used to generate answers |
| `JUDGE_MODEL` | LLM used by the TRACe evaluator (smaller/faster is fine) |
| `CHROMA_PERSIST_DIR` | **Absolute path** to ChromaDB storage directory |
| `HF_TOKEN` | HuggingFace token (required to download the ragbench dataset) |

Example:
```
PROVIDER=ollama
EMBEDDING_MODEL=nomic-embed-text-v2-moe:latest
GENERATOR_MODEL=gemma4:12b-it-q4_K_M
JUDGE_MODEL=llama3.1:8b-instruct-q4_K_M
CHROMA_PERSIST_DIR=/absolute/path/to/reliablerag/data/chroma_db
HF_TOKEN=hf_...
```

> `CHROMA_PERSIST_DIR` must be an absolute path. Relative paths resolve against the notebook's working directory which varies across environments.

---

## IDE setup

### PyCharm Pro

1. Open the project folder.
2. Click **"Set up uv environment"** in the banner — PyCharm will run `uv sync` and configure the interpreter automatically.
3. Alternatively: **Settings → Project → Python Interpreter → Add → Existing Environment** → select `.venv/bin/python`.

Make sure Ollama is running before executing any notebooks.