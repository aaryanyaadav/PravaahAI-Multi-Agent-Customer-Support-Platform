import json

from src.rag.parser.pdf_parser import (
    extract_text
)

from src.rag.chunking.chunker import (
    chunk_text
)
FAQ_PDF = (
    "src/rag/documents/faq/faq.pdf"
)

POLICY_PDF = (
    "src/rag/documents/policy/policy.pdf"
)
faq_text = extract_text(
    FAQ_PDF
)

policy_text = extract_text(
    POLICY_PDF
)
faq_chunks = chunk_text(
    faq_text
)

policy_chunks = chunk_text(
    policy_text
)
with open(
    "src/rag/parsed/faq_chunks.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        faq_chunks,
        f,
        indent=4
    )
with open(
    "src/rag/parsed/policy_chunks.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        policy_chunks,
        f,
        indent=4
    )
print(
    "Knowledge Base Built"
)