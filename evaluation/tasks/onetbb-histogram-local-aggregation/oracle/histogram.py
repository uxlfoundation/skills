"""Correct histogram implementation using partition-local aggregation."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor


def histogram(values: list[int], bins: int = 16, workers: int = 4) -> list[int]:
    def local_count(chunk: list[int]) -> list[int]:
        local = [0] * bins
        for value in chunk:
            local[value % bins] += 1
        return local

    chunks = [values[index::workers] for index in range(workers)]
    totals = [0] * bins
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for local in pool.map(local_count, chunks):
            for index, count in enumerate(local):
                totals[index] += count
    return totals


def reference_histogram(values: list[int], bins: int = 16) -> list[int]:
    counts = [0] * bins
    for value in values:
        counts[value % bins] += 1
    return counts


if __name__ == "__main__":
    data = [(index * 17 + 3) % 257 for index in range(1000)]
    print(histogram(data))
