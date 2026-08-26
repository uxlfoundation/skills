"""Optional oneDAL brute-force retrieval prototype."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from .benchmark import TOKEN_RE


class OnedalRetriever:
    """Binary bag-of-words retrieval through oneDAL NearestNeighbors."""

    name = "onedal"
    external_dependencies = 1

    def __init__(self) -> None:
        try:
            self.version = version("scikit-learn-intelex")
            import numpy as np
            from onedal.neighbors import NearestNeighbors
        except (PackageNotFoundError, ImportError) as exc:
            raise RuntimeError(
                "oneDAL retrieval is optional; install the version pinned in "
                "evaluation/agentic/requirements-onedal.txt"
            ) from exc
        self.np = np
        self.neighbors_type = NearestNeighbors
        self.document_ids: list[str] = []
        self.vocabulary: dict[str, int] = {}
        self.model = None

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return set(TOKEN_RE.findall(text.lower()))

    def _matrix(self, texts: list[str]):
        matrix = self.np.zeros((len(texts), len(self.vocabulary)), dtype=self.np.float32)
        for row, text in enumerate(texts):
            for token in self._tokens(text):
                column = self.vocabulary.get(token)
                if column is not None:
                    matrix[row, column] = 1.0
        return matrix

    def setup(self, corpus: list[dict[str, str]]) -> None:
        tokens = sorted({token for item in corpus for token in self._tokens(item["text"])})
        self.vocabulary = {token: index for index, token in enumerate(tokens)}
        self.document_ids = [item["id"] for item in corpus]
        matrix = self._matrix([item["text"] for item in corpus])
        self.model = self.neighbors_type(n_neighbors=1, algorithm="brute", metric="euclidean")
        self.model.fit(matrix)

    def retrieve_all(self, queries: list[str]) -> list[str]:
        if not queries:
            return []
        if self.model is None:
            raise RuntimeError("retriever is not initialized")
        query_matrix = self._matrix(queries)
        indices = self.model.kneighbors(query_matrix, n_neighbors=1, return_distance=False)
        return [self.document_ids[int(index)] for index in indices[:, 0]]
