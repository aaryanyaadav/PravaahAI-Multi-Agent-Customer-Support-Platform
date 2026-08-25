from src.rag.knowledge_base.knowledge_services import (
    KnowledgeService
)

def retrieve_faq(
    query: str
):
    return (
        KnowledgeService
        .retrieve(query)["faq"]
    )

def retrieve_policy(
    query: str
):
    return (
        KnowledgeService
        .retrieve(query)["policy"]
    )
