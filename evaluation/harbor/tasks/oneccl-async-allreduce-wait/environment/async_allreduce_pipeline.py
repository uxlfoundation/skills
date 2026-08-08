#!/usr/bin/env python3
"""Submit a batch of asynchronous allreduces. This starter is unsafe."""


def reduce_batches(comm, batches, *, max_inflight=2):
    send_buffer = []
    recv_buffer = []
    events = []
    results = []

    for batch in batches:
        send_buffer[:] = batch
        recv_buffer[:] = [0.0] * len(send_buffer)
        events.append(
            comm.allreduce(
                send_buffer,
                recv_buffer,
                len(send_buffer),
                "float32",
                "sum",
            )
        )
        results.append(list(recv_buffer))

    return results
