"""Optional LangGraph adapter for the UXL agentic reference workload."""

from __future__ import annotations

import threading
from dataclasses import asdict
from importlib.metadata import PackageNotFoundError, version
from typing import Any

from .benchmark import ToolResult, _run_tool


class LangGraphExecutor:
    """Run independent tool calls through LangGraph's Functional API runtime."""

    name = "langgraph"
    external_dependencies = 1

    def __init__(self, max_workers: int = 4) -> None:
        if max_workers < 1:
            raise ValueError("max_workers must be positive")
        self.max_workers = max_workers
        try:
            self.version = version("langgraph")
        except PackageNotFoundError as exc:
            raise RuntimeError(
                "LangGraph is optional; install the version pinned in "
                "evaluation/agentic/requirements-langgraph.txt"
            ) from exc

    def run(
        self,
        calls: list[dict[str, Any]],
        projects: dict[str, dict[str, str]],
        cancel: threading.Event,
    ) -> list[ToolResult]:
        if not calls:
            return []

        from langgraph.func import entrypoint, task

        @task(name="uxl_reference_tool")
        def execute(call: dict[str, Any]) -> dict[str, str]:
            return asdict(_run_tool(call, projects, cancel))

        @entrypoint()
        def workflow(tool_calls: list[dict[str, Any]]) -> list[dict[str, str]]:
            futures = [execute(call) for call in tool_calls]
            return [future.result() for future in futures]

        records = workflow.invoke(calls, config={"max_concurrency": self.max_workers})
        return sorted((ToolResult(**record) for record in records), key=lambda item: item.call_id)
