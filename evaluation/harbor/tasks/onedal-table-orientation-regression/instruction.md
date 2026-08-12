The oneDAL linear-regression pipeline in `/app/pipeline.py` receives training features from an ingestion layer as a list of feature columns. Model quality collapsed after that conversion, even though the public reproducer uses a square table and does not report a shape mismatch.

Run `python /app/reproduce.py`, diagnose the data contract at the oneDAL boundary, and repair `/app/pipeline.py`. Preserve the oneDAL estimator, its parameters, and the function interface. The repair must work for other sample and feature counts, not only the public fixture.
