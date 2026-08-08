Repair `/app/async_allreduce_pipeline.py`. It models a bounded pipeline of asynchronous oneCCL-style allreduce operations, but the starter consumes incomplete receive buffers and reuses live storage.

Preserve the public function `reduce_batches(comm, batches, *, max_inflight=2)`. For every input batch, call `comm.allreduce(send_buffer, recv_buffer, count, datatype, reduction)` exactly once with datatype `"float32"` and reduction `"sum"`. The returned event exposes `wait()`; the receive buffer is not valid until that call completes.

Return one independent result list per input batch in input order. Preserve every input batch. Keep each submitted send and receive buffer alive and unchanged until its event completes, wait every event exactly once before consuming its receive buffer, and never have more than `max_inflight` operations outstanding. Reject a boolean or integer value below one for `max_inflight` with `ValueError`. Do not add third-party dependencies or special-case the visible examples.

The verifier supplies deferred communicators and additional batch shapes. This task tests completion, buffer lifetime, bounded admission, and deterministic output ordering; it does not require a oneCCL installation.
