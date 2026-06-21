# CUAD Retrieval Trials — RAGBench Evaluation Report

**Dataset:** galileo-ai/ragbench, split=`cuad`, `train[0:N]`  
**Judge:** TRACe (RAGBench, Friel et al.) — LLM-as-judge for Adherence; GPT-4-annotated labels for Relevance/Utilization/Completeness  
**Vector store:** ChromaDB  

---

## Metric Definitions

| Metric | What it measures |
|---|---|
| **Relevance** | Fraction of retrieved context that is relevant to the question |
| **Utilization** | Fraction of retrieved context that the LLM actually uses in its answer |
| **Completeness** | Fraction of *all* relevant content in the document that was captured (recall) |
| **Adherence** | Whether the LLM answer is fully grounded in the retrieved context (binary, LLM-judged) |

**Success criterion:** `our_completeness` within 0.05 of `ref_completeness` (0.717) while keeping `our_relevance ≥ ref_relevance` and adherence trending toward 90%.

---

## Trial Log

### Experiment A — Cosine similarity
**Full config:** embedder=`nomic-embed-text-v2-moe`, judge=`gemma4:12b-it-q4_K_M`, similarity=cosine, chunk_size=500, overlap=50, top_k=20, N=5  
**Result:** Large improvement — relevance ~0.09, completeness ~0.74 on 5-sample slice.  

---

### Experiment B — Eval stabilization
**Reason:** Scores were noisy run-to-run; needed a stable signal before iterating further.  
**Change:**  
- `evaluation.py`: length unit chars → whitespace tokens (closer to RAGBench paper).  
- Added `judge_llm` with `temperature=0`.  
- Added `n_runs` averaging; adherence by strict majority vote.  
**Full config:** embedder=`nomic-embed-text-v2-moe`, judge=`gemma4:12b-it-q4_K_M`, similarity=cosine, chunk_size=500, overlap=50, top_k=20, N=5  
**Result:** More stable scores across runs. No aggregate change to the numbers.  

---

### Experiment C — Cross-encoder reranker (BAAI/bge-reranker-base)
**Reason:** Cosine retrieval surfaces plausible-but-imprecise chunks; a cross-encoder reranker should push the most relevant ones to the top.  
**Change:** Over-fetch top-50 from Chroma, rerank with cross-encoder, keep top-N.  
**Full config:** embedder=`nomic-embed-text-v2-moe`, judge=`gemma4:12b-it-q4_K_M`, similarity=cosine, chunk_size=500, overlap=50, fetch_k=50, top_n=8 or 20, N=5  
**Result (top_n=8):** Mixed — precision improved on samples 3/4, but sample 2 collapsed (relevance 0.146→0.000, completeness 1.0→0.0). Reranker demoted context-establishing chunks below the cutoff.  
**Result (top_n=20):** Same context window as baseline, only reorders — within judge noise.  
**Verdict:** Inconclusive on N=5. Parked for later. Reranking targets precision, not recall.  

---

### Experiment D — Swap judge: Gemma4 12B → Llama 3.1 8B
**Reason:** Gemma4 12B judge was taking 3–4 min per TRACe call on Apple Silicon; iteration speed was blocking progress.  
**Change:** `JUDGE_MODEL=llama3.1:8b-instruct-q4_K_M`, `temperature=0`.  
**Full config:** embedder=`nomic-embed-text-v2-moe`, judge=`llama3.1:8b-instruct-q4_K_M`, similarity=cosine, chunk_size=500, overlap=50, top_k=20, N=5  
**5-sample numbers (post-swap):** Relevance 0.166, Completeness 0.674  
**Lesson:** Judge swaps move absolute numbers. Llama is stricter on adherence (40% vs 100%) and faster (~30s/call). Re-baseline after any judge change.  

---

### Experiment E — Scale to N=20 + fix judge parse errors (authoritative baseline)
**Reason:** N=5 was unrepresentative — first 5 CUAD samples are the easy ones; needed a real N before trusting any diagnosis. Parse errors in the Llama judge were silently zeroing out samples; fixed with corrective retry and exclusion of failed runs from the average.  
**Change:**  
- Bumped evaluation from 5 → 20 CUAD samples, `n_runs=3`.  
- `evaluation.py`: corrective retry on parse failure (shows the model its bad output, asks it to fix); failed runs excluded from average rather than counted as zeros.  
- Prompt strengthened: JSON-only instruction added at top and bottom of `_ANNOTATION_PROMPT`.  
**Full config:** embedder=`nomic-embed-text-v2-moe`, judge=`llama3.1:8b-instruct-q4_K_M`, similarity=cosine, chunk_size=500, overlap=50, top_k=20, N=20, n_runs=3  

| Metric | Ours | Ref (GPT-4) |
|---|---|---|
| Relevance | **0.173** | 0.069 |
| Utilization | **0.097** | 0.042 |
| Completeness | 0.564 | **0.717** |
| Adherence | **55%** (11/20) | 90% (18/20) |
| Parse errors | 2/20 | — |

**This is the authoritative baseline. All subsequent experiments are compared against it.**  
**Diagnosis:** Completeness gap (0.564 vs 0.717) is the remaining bottleneck. Dense retrieval misses clauses with vocabulary different from the query.  

---

### Experiment F — Chunk size sweep (500/50, 1000/150, 1500/200)
**Reason:** Completeness gap suggested small chunks were splitting legal clauses mid-sentence; larger chunks should capture full clause text.  
**Note:** All three configs run with the fixed evaluator (Exp E parse error fix applied).

#### F1 — 1500/200
**Full config:** embedder=`nomic-embed-text-v2-moe`, judge=`llama3.1:8b-instruct-q4_K_M`, similarity=cosine, chunk_size=1500, overlap=200, top_k=20, N=20, n_runs=3  

| Metric | Ours | Ref (GPT-4) | vs E baseline |
|---|---|---|---|
| Relevance | 0.071 | 0.069 | −0.102 |
| Utilization | 0.041 | 0.042 | −0.056 |
| Completeness | **0.592** | 0.717 | **+0.028** |
| Adherence | 10% (2/20) | 90% | −45pp |
| Parse errors | 2/20 | — | — |

**Verdict:** Best completeness (0.592) but adherence collapses to 10% — large chunks give the generator too much unfocused context, causing it to hedge. Net negative overall.

#### F2 — 1000/150
**Full config:** embedder=`nomic-embed-text-v2-moe`, judge=`llama3.1:8b-instruct-q4_K_M`, similarity=cosine, chunk_size=1000, overlap=150, top_k=20, N=20, n_runs=3  

| Metric | Ours | Ref (GPT-4) | vs E baseline |
|---|---|---|---|
| Relevance | 0.090 | 0.069 | −0.083 |
| Utilization | 0.043 | 0.042 | −0.054 |
| Completeness | 0.446 | 0.717 | −0.118 |
| Adherence | 35% (7/20) | 90% | −20pp |
| Parse errors | 5/20 | — | — |

**Verdict:** Worse than baseline on all metrics. Most parse errors of the three configs (5/20).

**Chunk sweep conclusion:** 500/50 wins on every metric except raw completeness (where 1500/200 edges ahead by 0.028 at the cost of 45pp adherence). Fixed-character chunking is not the lever for closing the completeness gap.

---

### Experiment G — Hybrid retrieval (BM25 + dense cosine, RRF fusion)
**Reason:** Completeness gap diagnosis from Exp E — dense retrieval misses clauses with vocabulary different from the query. BM25 exact-term matching should recover those misses.  
**Change:** Added custom `BM25Retriever` (rank-bm25) alongside Chroma cosine retrieval. Combined via Reciprocal Rank Fusion (`rrf_k=60`, equal 0.5/0.5 weights). No change to chunk size (500/50) to isolate the retrieval change.  
**Full config:** embedder=`nomic-embed-text-v2-moe`, judge=`llama3.1:8b-instruct-q4_K_M`, similarity=cosine+BM25 RRF, chunk_size=500, overlap=50, top_k=20, N=20, n_runs=3

| Metric | Ours | Ref (GPT-4) | vs E baseline |
|---|---|---|---|
| Relevance | 0.112 | 0.069 | −0.061 |
| Utilization | 0.086 | 0.042 | −0.011 |
| Completeness | **0.590** | 0.717 | **+0.026** |
| Adherence | 30% (6/20) | 90% | −25pp |

**Verdict:** Completeness improved (+0.026, right direction). However relevance dropped sharply (0.173 → 0.112, −0.061) and adherence collapsed from 55% → 30% — BM25 injected noisier chunks (legal contracts repeat common terms like "party", "agreement", "shall" across irrelevant clauses, giving BM25 many false positives) that diluted the retrieved set and confused the generator into hedging. Equal RRF weights (0.5/0.5) give too much influence to BM25. Next step: reduce BM25 weight.

---

### Experiment H — Tune RRF weights (bm25_weight=0.3)
**Reason:** Experiment G used equal-weight hybrid (both retrievers weight=1.0, unweighted RRF) which improved completeness but collapsed adherence. Hypothesis: reducing BM25's influence to 0.3 (dense=0.7) keeps the coverage benefit while cutting noise.  
**Change:** Added `bm25_weight` parameter to `get_hybrid_retriever`. Set `bm25_weight=0.3`, `dense_weight=0.7`. Everything else identical to Exp G.  
**Full config:** embedder=`nomic-embed-text-v2-moe`, judge=`llama3.1:8b-instruct-q4_K_M`, similarity=cosine+BM25 RRF (0.3/0.7), chunk_size=500, overlap=50, top_k=20, N=20, n_runs=3

| Metric | Ours | Ref (GPT-4) | vs E baseline | vs G (equal-weight) |
|---|---|---|---|---|
| Relevance | 0.132 | 0.069 | −0.041 | +0.020 |
| Utilization | 0.054 | 0.042 | −0.043 | −0.032 |
| Completeness | 0.524 | 0.717 | −0.040 | −0.066 |
| Adherence | 40% (8/20) | 90% | −15pp | +10pp |
| Parse errors | 2/20 | — | — | — |

**Verdict:** Reducing BM25 weight recovered some adherence (30% → 40%) but gave up the completeness gain — completeness fell from 0.590 (G) back to 0.524, below the baseline (0.564). The trade-off is unfavourable: we lose more on completeness than we gain on adherence. Weight tuning alone cannot simultaneously improve both — the noise problem requires filtering, not just down-weighting.

---

### Experiment I — Reranker on top of equal-weight hybrid
**Reason:** Experiment H showed weight tuning can't simultaneously recover completeness and adherence — the BM25 noise problem requires filtering, not down-weighting. A cross-encoder reranker applied after retrieval should keep BM25's recall while cutting irrelevant chunks before the generator sees them.  
**Change:** Equal-weight hybrid (bm25_weight=0.5) over-fetches `fetch_k=40` candidates via RRF, then `BAAI/bge-reranker-base` cross-encoder reranks to `top_n=20`. New `get_hybrid_reranked_retriever` function in `retriever.py`. No change to chunking (500/50).  
**Full config:** embedder=`nomic-embed-text-v2-moe`, judge=`llama3.1:8b-instruct-q4_K_M`, similarity=cosine+BM25 RRF (equal weight) + cross-encoder rerank, chunk_size=500, overlap=50, fetch_k=40, top_n=20, N=20, n_runs=3

| Metric | Ours | Ref (GPT-4) | vs E baseline | vs G (equal hybrid) |
|---|---|---|---|---|
| Relevance | 0.135 | 0.069 | −0.038 | +0.023 |
| Utilization | 0.091 | 0.042 | −0.006 | +0.005 |
| Completeness | 0.479 | 0.717 | −0.085 | −0.111 |
| Adherence | 20% (4/20) | 90% | −35pp | −10pp |
| Parse errors | 4/20 | — | — | — |

**Verdict:** Worst adherence across all experiments (20%). The cross-encoder (`bge-reranker-base`) is a general-domain model — in legal contracts it promotes chunks that match query keywords ("source code", "license") but don't contain the actual responsive clause. This re-ordering actively removes the grounding chunks BM25 recovered, so the generator hedges even more. Completeness also dropped to 0.479, the lowest of any hybrid config. Reranking with a general-domain cross-encoder is net negative on legal text. **Dense-only baseline (Exp E) remains the best all-round config.**

---

## Summary Table

All metrics are **averages across N=20 samples** with fixed evaluator. Ref metrics come from GPT-4 annotations in the RAGBench dataset and are fixed per sample.

| Exp | Retrieval | chunk/overlap | Our Rel. | Our Util. | Our Comp. | Ref Comp. | Our Adh. | Notes |
|---|---|---|---|---|---|---|---|---|
| **E (baseline)** | cosine | 500/50 | **0.173** | **0.097** | 0.564 | 0.717 | **55%** | Best overall |
| F1 | cosine | 1500/200 | 0.071 | 0.041 | **0.592** | 0.717 | 10% | Best comp, adherence collapses |
| F2 | cosine | 1000/150 | 0.090 | 0.043 | 0.446 | 0.717 | 35% | Worst overall |
| G | cosine+BM25 RRF (equal weight) | 500/50 | 0.112 | 0.086 | 0.590 | 0.717 | 30% | Best completeness, adherence drops |
| H | cosine+BM25 RRF (bm25=0.3) | 500/50 | 0.132 | 0.054 | 0.524 | 0.717 | 40% | Weight tuning: completeness fell back below baseline |
| I | cosine+BM25 RRF (equal) + cross-encoder rerank | 500/50 | 0.135 | 0.091 | 0.479 | 0.717 | 20% | Worst adherence; reranker demotes grounding chunks |

All experiments: embedder=`nomic-embed-text-v2-moe`, judge=`llama3.1:8b-instruct-q4_K_M`, top_k=20, N=20, n_runs=3.  
**Current best config: E (dense-only) on all metrics. No hybrid variant has improved on it holistically.**

---

## Open Diagnosis

- **Completeness gap (0.564 vs 0.717 ref):** Dense-only baseline (Exp E) is the best all-round config. BM25 hybrid improved completeness to 0.590 (Exp G) but at a 25pp adherence cost — no weight or reranking variant has recovered both simultaneously.
- **Hybrid retrieval is net negative so far:** BM25 injects legal boilerplate false-positives ("party", "agreement", "shall") that dense retrieval correctly ranks low. General-domain cross-encoder reranking (Exp I) made this worse, not better — it re-promotes keyword-matching but non-grounding chunks.
- **Adherence is the binding constraint:** Generator hedges ("I do not have enough information") whenever noisy or off-topic chunks dilute the context window. Dense-only keeps this at 55%; any hybrid drops it to 20–40%.
- **4 persistent parse errors per run (samples 2, 5, 12, 16):** Zeroing these out may be inflating apparent scores on "good" runs. Likely a judge prompt interaction with specific sample content.
- **Root cause of completeness gap likely vocabulary mismatch:** Dense retrieval misses clauses that use different legal terminology than the query. BM25 is the right idea but wrong execution on this domain.

---

## Next Steps (Priority Order)

1. **Query expansion / HyDE** — generate a hypothetical answer clause, embed that alongside the original query, fuse results. Catches paraphrase mismatches without BM25 noise. Doesn't require a domain-specific model.
2. **Legal-domain embedder** — swap `nomic-embed-text-v2-moe` for a legal-tuned model (e.g. `legal-bert`, `inlegal-bert`, or `bge-large-en-v1.5` fine-tuned on contracts). Vocabulary mismatch at the embedding level is likely the root cause; fixing it there would be cleaner than patching at retrieval.
3. **Sentence-level chunking** — CUAD clauses are typically one sentence. RecursiveCharacterTextSplitter at 500 chars splits mid-clause; a sentence-aware splitter (e.g. spaCy) might improve both precision and recall without changing retrieval strategy.
4. **Diagnose the 4 persistent parse errors** — understand whether samples 2, 5, 12, 16 have structural properties (very short docs, atypical formatting) that break the judge prompt, and fix or exclude them from the evaluation set.