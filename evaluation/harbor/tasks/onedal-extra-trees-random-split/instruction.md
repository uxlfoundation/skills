Repair the ExtraTrees regression failure in the pinned oneDAL source at `/app/oneDAL`.

The public reproducer trains a one-tree decision-forest regressor with the random splitter and `bootstrap=false`, then predicts its training data. It should fit that data exactly, but the current source stops splitting after only a handful of leaves and reports a large mean-squared error.

Run `/app/reproduce.sh` before and after your repair. Preserve the random-split algorithm and the public reproducer. Make the smallest source-level correction that restores valid variance-based split selection for both weighted and unweighted data. Do not special-case the supplied dataset or change the estimator configuration. Briefly explain the observed failure, root cause, repair, and verification.
