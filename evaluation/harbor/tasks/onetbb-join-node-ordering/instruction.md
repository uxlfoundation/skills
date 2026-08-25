Repair the ordering bug in `/app/join_pipeline.cpp`.

The program models a reported oneTBB flow-graph incident. A first `queueing` `join_node` creates matching token pairs, but successor delivery through a parallel stage does not preserve input order. The current graph then feeds those arrivals into another `queueing` join alongside an ordered stream, so unrelated tokens are paired when more than one worker is active.

Preserve the public `run_join_pipeline(std::size_t)` interface and the oneTBB flow graph. Every source token must be emitted exactly once with the counterpart having the same value. Do not solve the problem by globally limiting oneTBB to one thread. Use a graph-level ordering or correlation mechanism, run the supplied checks, and briefly explain the incorrect assumption and the validation performed.
