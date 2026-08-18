import json

# pyrefly: ignore [missing-import]
from rank_bm25 import BM25Okapi

class BM25Retriever:

    def __init__(
        self,
        file_path
    ):

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as f:

            self.chunks = (
                json.load(f)
            )

        self.tokenized = [

            chunk.lower().split()

            for chunk
            in self.chunks
        ]

        self.bm25 = BM25Okapi(
            self.tokenized
        )

    def search(
        self,
        query,
        k=3
    ):

        tokens = (
            query.lower().split()
        )

        scores = (
            self.bm25.get_scores(
                tokens
            )
        )

        ranked = sorted(

            zip(
                self.chunks,
                scores
            ),

            key=lambda x: x[1],

            reverse=True
        )

        return [

            chunk

            for chunk, score

            in ranked[:k]
        ]
