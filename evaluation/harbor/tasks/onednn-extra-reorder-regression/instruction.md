Repair the repeated weight-layout conversion in `/app/weight_reorder.cpp`.

The program performs batched inference with a real oneDNN convolution. It correctly lets the primitive descriptor select an optimized weight layout, but it rebuilds and reorders the same constant weights before every inference iteration. That framework/library boundary creates redundant oneDNN work.

Run `bash /app/reproduce.sh`, preserve the command-line interface, `format_tag::any` weight selection, actual oneDNN convolution, and numerical results, then make the transformed constant weights reusable across iterations. Do not force the primitive to use the user `oihw` layout, remove the convolution, suppress oneDNN verbose output, or claim a hardware speedup. Briefly explain which memory is framework-owned, which layout is selected by oneDNN, and why the reorder is valid to cache.
