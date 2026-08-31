# Retained evaluation cells

Store accepted matched-comparison records here as `<cell_id>.json`. Each record must satisfy [`schemas/evaluation-cell.schema.json`](../../../../schemas/evaluation-cell.schema.json), belong to a declared skill/task pair, and contain only sanitized summary evidence.

Generate a record with `scripts/compare_harbor_skill.ps1`, review it with its Harbor jobs and Markdown comparison, then copy only the accepted JSON record here. Raw trajectories, private-machine details, credentials, and unsanitized logs do not belong in this public directory.

Run `python scripts/validate_evaluation_cells.py` before committing. Older or superseded records remain historical evidence; the dashboard determines currentness from the recorded time, declared maximum age, and material dimensions.
