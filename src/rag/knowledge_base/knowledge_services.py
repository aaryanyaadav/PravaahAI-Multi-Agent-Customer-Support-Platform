from src.rag.retriever.bm25_retriever import (
    BM25Retriever
)
faq_retriever = BM25Retriever(
    "src/rag/parsed/faq_chunks.json"
)

policy_retriever = BM25Retriever(
    "src/rag/parsed/policy_chunks.json"
)

class KnowledgeService:
    @staticmethod
    def retrieve(
        query
    ):

        faq_results = (
            faq_retriever.search(
                query
            )
        )

        policy_results = (
            policy_retriever.search(
                query
            )
        )

        return {

            "faq":
            faq_results,

            "policy":
            policy_results
        }