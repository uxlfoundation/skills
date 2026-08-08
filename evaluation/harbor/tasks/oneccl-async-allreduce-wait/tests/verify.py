#!/usr/bin/env python3
"""Behavioral verifier for bounded asynchronous allreduce completion."""

from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import sys


class DeferredEvent:
    def __init__(self, comm, send_buffer, recv_buffer):
        self.comm = comm
        self.send_buffer = send_buffer
        self.recv_buffer = recv_buffer
        self.snapshot = list(send_buffer)
        self.wait_count = 0

    def wait(self):
        assert self.wait_count == 0, "event waited more than once"
        assert self.send_buffer == self.snapshot, "live send buffer was mutated"
        self.wait_count += 1
        self.recv_buffer[:] = [self.comm.world_size * value for value in self.snapshot]
        self.comm.outstanding -= 1


class DeferredCommunicator:
    def __init__(self, *, world_size, limit):
        self.world_size = world_size
        self.limit = limit
        self.outstanding = 0
        self.max_seen = 0
        self.events = []

    def allreduce(self, send_buffer, recv_buffer, count, datatype, reduction):
        assert isinstance(send_buffer, list), "send buffer must be owned storage"
        assert isinstance(recv_buffer, list), "receive buffer must be owned storage"
        assert send_buffer is not recv_buffer, "expected an out-of-place collective"
        assert count == len(send_buffer) == len(recv_buffer), "count/buffer mismatch"
        assert datatype == "float32", datatype
        assert reduction == "sum", reduction
        self.outstanding += 1
        self.max_seen = max(self.max_seen, self.outstanding)
        assert self.outstanding <= self.limit, "too many collectives in flight"
        event = DeferredEvent(self, send_buffer, recv_buffer)
        self.events.append(event)
        return event


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("async_allreduce_pipeline", path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assert_run(module, batches, *, limit, world_size):
    original = copy.deepcopy(batches)
    comm = DeferredCommunicator(world_size=world_size, limit=limit)
    results = module.reduce_batches(comm, batches, max_inflight=limit)
    expected = [[world_size * value for value in batch] for batch in original]
    assert results == expected, (results, expected)
    assert batches == original, "input batches were mutated"
    assert comm.outstanding == 0, "collectives returned without completion"
    assert all(event.wait_count == 1 for event in comm.events), "every event must be waited once"
    assert comm.max_seen <= limit, (comm.max_seen, limit)
    assert len({id(result) for result in results}) == len(results), "result buffers alias"
    return comm


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        raise SystemExit("usage: verify.py SCRIPT")
    module = load_module(Path(argv[1]))

    comm = assert_run(
        module,
        [[1.0, 2.5], [3.0], [], [-4.0, 0.5, 8.0]],
        limit=2,
        world_size=3,
    )
    assert comm.max_seen == 2, "implementation did not exercise bounded overlap"
    assert_run(module, [[1.0], [2.0], [3.0]], limit=1, world_size=4)

    for invalid in (0, -1, True):
        try:
            module.reduce_batches(DeferredCommunicator(world_size=2, limit=1), [], max_inflight=invalid)
        except ValueError:
            pass
        else:
            raise AssertionError(f"max_inflight={invalid!r} was not rejected")

    print("async allreduce verifier passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
