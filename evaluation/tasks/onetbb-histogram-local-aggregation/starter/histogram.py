"""Buggy histogram task used by the UXL executable evaluator.

The update below models the common oneTBB mistake of mutating one shared
histogram from parallel workers without a safe reduction pattern.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor


def histogram(values: list[int], bins: int = 16, workers: int = 4) -> list[int]:
    counts = [0] * bins

    def update(chunk: list[int]) -> None:
        for value in chunk:
            bucket = value % bins
            current = counts[bucket]
            # A parallel C++ version of this shape would be a data race.
            counts[bucket] = current + 1

    chunks = [values[index::workers] for index in range(workers)]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(update, chunks))
    return counts


def reference_histogram(values: list[int], bins: int = 16) -> list[int]:
    counts = [0] * bins
    for value in values:
        counts[value % bins] += 1
    return counts


if __name__ == "__main__":
    data = [(index * 17 + 3) % 257 for index in range(1000)]
    print(histogram(data))
