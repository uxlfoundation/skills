from __future__ import annotations

import argparse
import concurrent.futures
import json
import math
import os
import platform
import re
import statistics
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Protocol


TOKEN_RE = re.compile(r"[a-z0-9]+")
CONTRACT_PATH = Path(__file__).with_name("workload.json")
STAGES = ("plan", "retrieval", "tool_execution", "synthesis", "end_to_end")


class WorkloadError(RuntimeError):
    """Base error for workload contract failures."""


class WorkloadCancelled(WorkloadError):
    """Raised when a run is cancelled."""


class ToolExecutionError(WorkloadError):
    def __init__(self, call_id: str, message: str) -> None:
        super().__init__(f"tool call {call_id!r} failed: {message}")
        self.call_id = call_id


@dataclass(frozen=True)
class ToolResult:
    call_id: str
    project: str
    display_name: str
    status: str


class Executor(Protocol):
    name: str

    def run(
        self,
        calls: list[dict[str, Any]],
        projects: dict[str, dict[str, str]],
        cancel: threading.Event,
    ) -> list[ToolResult]: ...


class Retriever(Protocol):
    name: str
    external_dependencies: int

    def setup(self, corpus: list[dict[str, str]]) -> None: ...

    def retrieve_all(self, queries: list[str]) -> list[str]: ...


def _run_tool(
    call: dict[str, Any],
    projects: dict[str, dict[str, str]],
    cancel: threading.Event,
) -> ToolResult:
    call_id = str(call["id"])
    if cancel.is_set():
        raise WorkloadCancelled(f"tool call {call_id!r} cancelled")
    if call.get("tool") == "raise_expected":
        raise ToolExecutionError(call_id, "expected failure")
    if call.get("tool") != "project_status":
        raise ToolExecutionError(call_id, f"unknown tool {call.get('tool')!r}")

    remaining = int(call.get("delay_ms", 0))
    while remaining > 0:
        if cancel.is_set():
            raise WorkloadCancelled(f"tool call {call_id!r} cancelled")
        step = min(remaining, 2)
        time.sleep(step / 1000)
        remaining -= step

    project = str(call["project"])
    try:
        record = projects[project]
    except KeyError as exc:
        raise ToolExecutionError(call_id, f"unknown project {project!r}") from exc
    return ToolResult(call_id, project, record["display_name"], record["status"])


class SerialExecutor:
    name = "serial"
    external_dependencies = 0

    def run(
        self,
        calls: list[dict[str, Any]],
        projects: dict[str, dict[str, str]],
        cancel: threading.Event,
    ) -> list[ToolResult]:
        return [_run_tool(call, projects, cancel) for call in calls]


class ThreadedExecutor:
    name = "threaded"
    external_dependencies = 0

    def __init__(self, max_workers: int = 4) -> None:
        if max_workers < 1:
            raise ValueError("max_workers must be positive")
        self.max_workers = max_workers

    def run(
        self,
        calls: list[dict[str, Any]],
        projects: dict[str, dict[str, str]],
        cancel: threading.Event,
    ) -> list[ToolResult]:
        if not calls:
            return []
        results: list[ToolResult] = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            futures = {
                pool.submit(_run_tool, call, projects, cancel): str(call["id"])
                for call in calls
            }
            try:
                for future in concurrent.futures.as_completed(futures):
                    results.append(future.result())
            except BaseException:
                cancel.set()
                for pending in futures:
                    pending.cancel()
                for pending in futures:
                    if pending.done() and not pending.cancelled():
                        try:
                            pending.exception()
                        except concurrent.futures.CancelledError:
                            pass
                raise
        return sorted(results, key=lambda item: item.call_id)


def _tokens(text: str) -> set[str]:
    return set(TOKEN_RE.findall(text.lower()))


def _retrieve(query: str, corpus: list[dict[str, str]]) -> str:
    query_tokens = _tokens(query)
    scored = []
    for document in corpus:
        doc_tokens = _tokens(document["text"])
        intersection = len(query_tokens & doc_tokens)
        union = len(query_tokens | doc_tokens)
        score = intersection / union if union else 0.0
        scored.append((score, intersection, document["id"]))
    return max(scored)[2]


class LexicalRetriever:
    name = "lexical"
    external_dependencies = 0

    def __init__(self) -> None:
        self.corpus: list[dict[str, str]] = []

    def setup(self, corpus: list[dict[str, str]]) -> None:
        self.corpus = corpus

    def retrieve_all(self, queries: list[str]) -> list[str]:
        return [_retrieve(query, self.corpus) for query in queries]


def _percentile(values: list[float], percentile: int) -> float:
    if not values:
        raise ValueError("cannot calculate percentile of an empty series")
    ordered = sorted(values)
    index = max(0, math.ceil(percentile / 100 * len(ordered)) - 1)
    return ordered[index]


class BenchmarkRunner:
    def __init__(
        self,
        contract: dict[str, Any],
        executor: Executor,
        retriever: Retriever | None = None,
    ) -> None:
        self.contract = contract
        self.executor = executor
        self.retriever = retriever or LexicalRetriever()
        self._validate_contract()
        setup_started = time.monotonic_ns()
        self.retriever.setup(self.contract["corpus"])
        self.retriever_setup_ms = (time.monotonic_ns() - setup_started) / 1_000_000

    @classmethod
    def from_path(
        cls,
        path: Path,
        executor: Executor,
        retriever: Retriever | None = None,
    ) -> "BenchmarkRunner":
        return cls(json.loads(path.read_text(encoding="utf-8")), executor, retriever)

    def _validate_contract(self) -> None:
        if self.contract.get("schema_version") != "1.0":
            raise WorkloadError("unsupported workload schema")
        if tuple(self.contract.get("measurement", {}).get("stages", [])) != STAGES:
            raise WorkloadError("timing stage contract does not match the runner")
        scenario_ids = [scenario["id"] for scenario in self.contract.get("scenarios", [])]
        if len(scenario_ids) != len(set(scenario_ids)) or not scenario_ids:
            raise WorkloadError("scenario ids must be unique and non-empty")

    def run_scenario(self, scenario: dict[str, Any]) -> dict[str, Any]:
        timings: dict[str, float] = {}
        started = time.monotonic_ns()

        stage = time.monotonic_ns()
        queries = [str(query) for query in scenario.get("queries", [])]
        calls = [dict(call) for call in scenario.get("tool_calls", [])]
        timings["plan"] = (time.monotonic_ns() - stage) / 1_000_000

        stage = time.monotonic_ns()
        routes: list[str] = []
        passes = int(scenario.get("retrieval_passes", 0))
        for _ in range(passes):
            routes = self.retriever.retrieve_all(queries)
        timings["retrieval"] = (time.monotonic_ns() - stage) / 1_000_000

        stage = time.monotonic_ns()
        results = self.executor.run(calls, self.contract["projects"], threading.Event())
        timings["tool_execution"] = (time.monotonic_ns() - stage) / 1_000_000

        stage = time.monotonic_ns()
        answer = self._synthesize(scenario["shape"], routes, results)
        timings["synthesis"] = (time.monotonic_ns() - stage) / 1_000_000
        timings["end_to_end"] = (time.monotonic_ns() - started) / 1_000_000

        expected = scenario["expected"]
        passed = routes == expected["routes"] and answer == expected["answer"]
        return {
            "scenario_id": scenario["id"],
            "shape": scenario["shape"],
            "passed": passed,
            "routes": routes,
            "answer": answer,
            "timings_ms": {stage_name: round(timings[stage_name], 6) for stage_name in STAGES},
        }

    @staticmethod
    def _synthesize(shape: str, routes: list[str], results: list[ToolResult]) -> str:
        if shape == "short-turn":
            result = results[0]
            return f"{result.display_name} is {result.status}; route={routes[0]}."
        if shape == "tool-fan-out":
            values = sorted(f"{result.display_name}={result.status}" for result in results)
            return "; ".join(values) + "."
        if shape == "retrieval-heavy":
            return "routes=" + ",".join(routes) + "."
        raise WorkloadError(f"unknown shape {shape!r}")

    def verify_failure_paths(self) -> dict[str, str]:
        projects = self.contract["projects"]

        pre_cancelled = threading.Event()
        pre_cancelled.set()
        try:
            self.executor.run(
                [{"id": "cancel-control", "tool": "project_status", "project": "onetbb"}],
                projects,
                pre_cancelled,
            )
        except WorkloadCancelled:
            cancelled_result = "pass"
        else:
            cancelled_result = "fail"

        try:
            self.executor.run(
                [{"id": "failure-control", "tool": "raise_expected"}],
                projects,
                threading.Event(),
            )
        except ToolExecutionError as exc:
            failure_result = "pass" if exc.call_id == "failure-control" else "fail"
        else:
            failure_result = "fail"

        return {"pre_cancelled": cancelled_result, "tool_exception": failure_result}

    def run(self, repetitions: int, warmups: int) -> dict[str, Any]:
        if repetitions < 1 or warmups < 0:
            raise ValueError("repetitions must be positive and warmups non-negative")

        for _ in range(warmups):
            for scenario in self.contract["scenarios"]:
                result = self.run_scenario(scenario)
                if not result["passed"]:
                    raise WorkloadError(f"warmup correctness failed for {scenario['id']}")

        runs = []
        for _ in range(repetitions):
            for scenario in self.contract["scenarios"]:
                runs.append(self.run_scenario(scenario))

        failure_checks = self.verify_failure_paths()
        all_passed = all(run["passed"] for run in runs) and all(
            result == "pass" for result in failure_checks.values()
        )
        summaries: dict[str, Any] = {}
        for scenario in self.contract["scenarios"]:
            scenario_runs = [run for run in runs if run["scenario_id"] == scenario["id"]]
            stage_summary = {}
            for stage in STAGES:
                values = [run["timings_ms"][stage] for run in scenario_runs]
                stage_summary[stage] = {
                    "median_ms": round(statistics.median(values), 6),
                    "p50_ms": round(_percentile(values, 50), 6),
                    "p95_ms": round(_percentile(values, 95), 6),
                }
            summaries[scenario["id"]] = {
                "shape": scenario["shape"],
                "verified_successes": sum(run["passed"] for run in scenario_runs),
                "attempts": len(scenario_runs),
                "stages": stage_summary,
            }

        return {
            "schema_version": "1.0",
            "contract_id": self.contract["contract_id"],
            "executor": self.executor.name,
            "retriever": self.retriever.name,
            "configuration": {
                "repetitions": repetitions,
                "warmups": warmups,
                "external_dependencies": (
                    getattr(self.executor, "external_dependencies", 0)
                    + getattr(self.retriever, "external_dependencies", 0)
                ),
                "external_model_calls": 0,
                "cost_usd": 0.0,
                "retriever_setup_ms": round(self.retriever_setup_ms, 6),
            },
            "environment": {
                "python": platform.python_version(),
                "implementation": platform.python_implementation(),
                "platform": platform.platform(),
                "logical_cpus": os.cpu_count(),
            },
            "correctness": {"passed": all_passed, "failure_paths": failure_checks},
            "scenarios": summaries,
            "runs": runs,
        }


def _executor_from_args(name: str, max_workers: int) -> Executor:
    if name == "serial":
        return SerialExecutor()
    if name == "threaded":
        return ThreadedExecutor(max_workers=max_workers)
    if name == "langgraph":
        from .langgraph_adapter import LangGraphExecutor

        return LangGraphExecutor(max_workers=max_workers)
    raise ValueError(f"unknown executor {name!r}")


def _retriever_from_args(name: str) -> Retriever:
    if name == "lexical":
        return LexicalRetriever()
    if name == "onedal":
        from .onedal_retriever import OnedalRetriever

        return OnedalRetriever()
    raise ValueError(f"unknown retriever {name!r}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=CONTRACT_PATH)
    parser.add_argument("--executor", choices=("serial", "threaded", "langgraph"), default="serial")
    parser.add_argument("--retriever", choices=("lexical", "onedal"), default="lexical")
    parser.add_argument("--max-workers", type=int, default=4)
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--summary-only", action="store_true")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    executor = _executor_from_args(args.executor, args.max_workers)
    retriever = _retriever_from_args(args.retriever)
    runner = BenchmarkRunner.from_path(args.contract, executor, retriever)
    report = runner.run(args.repetitions, args.warmups)
    if args.summary_only:
        report = {key: value for key, value in report.items() if key != "runs"}
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if report["correctness"]["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
