#!/usr/bin/env python3
"""Run a bounded pipeline of asynchronous allreduces safely."""


def reduce_batches(comm, batches, *, max_inflight=2):
    if isinstance(max_inflight, bool) or not isinstance(max_inflight, int) or max_inflight < 1:
        raise ValueError("max_inflight must be a positive integer")

    pending = []
    results = []

    def complete_oldest():
        index, event, send_buffer, recv_buffer = pending.pop(0)
        event.wait()
        results[index] = list(recv_buffer)
        # Keeping both buffers in the pending record makes their lifetime explicit.
        del send_buffer

    for batch in batches:
        send_buffer = list(batch)
        recv_buffer = [0.0] * len(send_buffer)
        index = len(results)
        results.append(None)
        event = comm.allreduce(
            send_buffer,
            recv_buffer,
            len(send_buffer),
            "float32",
            "sum",
        )
        pending.append((index, event, send_buffer, recv_buffer))
        if len(pending) >= max_inflight:
            complete_oldest()

    while pending:
        complete_oldest()

    return results
