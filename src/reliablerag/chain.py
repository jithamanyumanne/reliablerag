import time

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableLambda, RunnableParallel, RunnablePassthrough
from langchain_core.vectorstores import VectorStoreRetriever

_RAG_PROMPT_TEMPLATE: str = """\
You are a helpful assistant. Use the following pieces of retrieved context to answer the question.
If you don't know the answer, say that you don't know. Use three sentences maximum and keep the answer concise.

Context:
{context}

Question: {question}

Answer:"""


class TimingCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self._llm_t0 = None
        self._retriever_t0 = None

    def on_retriever_start(self, serialized, query, **kwargs):
        self._retriever_t0 = time.perf_counter()

    def on_retriever_end(self, documents, **kwargs):
        print(f"[timing] retriever: {time.perf_counter() - self._retriever_t0:.3f}s")

    def on_chat_model_start(self, serialized, messages, **kwargs):
        self._llm_t0 = time.perf_counter()

    def on_llm_end(self, response, **kwargs):
        print(f"[timing] llm      : {time.perf_counter() - self._llm_t0:.3f}s")


def _format_docs(docs: list) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


def build_rag_chain(
    retriever: VectorStoreRetriever,
    llm: BaseChatModel,
    prompt_template: str = _RAG_PROMPT_TEMPLATE,
) -> Runnable:
    prompt = ChatPromptTemplate.from_template(prompt_template)

    chain = (
        RunnableParallel({"context": retriever | RunnableLambda(_format_docs), "question": RunnablePassthrough()})
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain
