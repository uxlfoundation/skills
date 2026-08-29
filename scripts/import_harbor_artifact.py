#!/usr/bin/env python3
"""Safely import downloaded Harbor CI artifacts into the local jobs directory."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import stat
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

from validate_target_qualification import validate_record


@dataclass(frozen=True)
class ImportOutcome:
    jobs: list[tuple[str, Path]]
    qualification_candidates: list[tuple[str, Path]]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def is_harbor_job_result(path: Path) -> bool:
    value = load_json(path)
    return bool(
        value
        and isinstance(value.get("n_total_trials"), int)
        and isinstance(value.get("stats"), dict)
    )


def safe_zip_path(name: str) -> PurePosixPath:
    normalized = name.replace("\\", "/")
    path = PurePosixPath(normalized)
    if (
        not normalized
        or path.is_absolute()
        or any(part == ".." for part in path.parts)
        or re.match(r"^[A-Za-z]:", normalized)
    ):
        raise ValueError(f"unsafe archive path: {name!r}")
    return path


def extract_zip_safely(archive: Path, destination: Path) -> None:
    destination_resolved = destination.resolve()
    with zipfile.ZipFile(archive) as bundle:
        for item in bundle.infolist():
            relative = safe_zip_path(item.filename)
            mode = (item.external_attr >> 16) & 0o170000
            if stat.S_ISLNK(mode):
                raise ValueError(f"archive contains a symbolic link: {item.filename!r}")
            target = destination.joinpath(*relative.parts).resolve()
            try:
                target.relative_to(destination_resolved)
            except ValueError as exc:
                raise ValueError(f"archive path escapes destination: {item.filename!r}") from exc
            if item.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with bundle.open(item) as source, target.open("wb") as output:
                shutil.copyfileobj(source, output)


def reject_symlinks(directory: Path) -> None:
    for path in directory.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"artifact directory contains a symbolic link: {path}")


def find_job_roots(directory: Path) -> list[Path]:
    roots = [
        result.parent
        for result in directory.rglob("result.json")
        if is_harbor_job_result(result)
    ]
    unique = {root.resolve(): root for root in roots}
    return sorted(unique.values(), key=lambda path: str(path).lower())


def ensure_within(path: Path, parent: Path) -> None:
    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError as exc:
        raise ValueError(f"destination escapes jobs directory: {path}") from exc


def qualification_evidence_errors(record: dict[str, Any], artifact_root: Path) -> list[str]:
    evidence = record["evidence"]
    scope = record["scope"]
    lane = record["lane"]
    matching_results = [
        path
        for path in artifact_root.rglob("result.json")
        if is_harbor_job_result(path) and sha256(path) == evidence["result_sha256"]
    ]
    if not matching_results:
        return ["record.evidence.result_sha256 does not match a Harbor result in the artifact"]

    provenance_matches: list[Path] = []
    for path in artifact_root.rglob("runner-provenance.json"):
        if sha256(path) == evidence["provenance_sha256"]:
            provenance_matches.append(path)
    if not provenance_matches:
        return ["record.evidence.provenance_sha256 does not match provenance in the artifact"]

    binding_errors: list[str] = []
    for provenance_path in provenance_matches:
        provenance = load_json(provenance_path)
        if not provenance:
            continue
        task = provenance.get("task")
        oracle = provenance.get("oracle")
        if not isinstance(task, dict) or not isinstance(oracle, dict):
            continue
        if provenance.get("source_commit") != scope["task_revision"]["commit"]:
            continue
        if provenance.get("adapter_id") != lane["adapter_id"]:
            continue
        if (
            task.get("skill") != scope["skill"]
            or task.get("name") != scope["task"]
            or task.get("hardware_class") != lane["hardware_class"]
        ):
            continue
        if oracle.get("status") != "passed" or not isinstance(oracle.get("result_path"), str):
            continue
        try:
            relative_result = safe_zip_path(oracle["result_path"])
            declared_result = provenance_path.parent.joinpath(*relative_result.parts).resolve()
            declared_result.relative_to(provenance_path.parent.resolve())
        except ValueError:
            continue
        if declared_result in {path.resolve() for path in matching_results}:
            return []
    binding_errors.append(
        "qualification does not match the adapter, task, commit, hardware class, and passed oracle "
        "declared by its hashed provenance"
    )
    return binding_errors


def find_qualification_candidates(
    artifact_root: Path,
) -> list[tuple[Path, dict[str, Any]]]:
    candidates: list[tuple[Path, dict[str, Any]]] = []
    ids: set[str] = set()
    for path in sorted(artifact_root.rglob("qualification-record.json")):
        record = load_json(path)
        if record is None:
            raise ValueError(f"qualification candidate is not a JSON object: {path}")
        errors = validate_record(record)
        if not errors:
            errors.extend(qualification_evidence_errors(record, artifact_root))
        if errors:
            detail = "; ".join(errors)
            raise ValueError(f"qualification candidate failed validation ({path}): {detail}")
        qualification_id = record["qualification_id"]
        if qualification_id in ids:
            raise ValueError(f"artifact contains duplicate qualification id: {qualification_id}")
        ids.add(qualification_id)
        candidates.append((path, record))
    return candidates


def stage_qualification_candidates(
    candidates: list[tuple[Path, dict[str, Any]]], review_dir: Path
) -> list[tuple[str, Path]]:
    if not candidates:
        return []
    review_dir.mkdir(parents=True, exist_ok=True)
    staged: list[tuple[str, Path]] = []
    for _, record in candidates:
        destination = review_dir / f"{record['qualification_id']}.json"
        ensure_within(destination, review_dir)
        content = json.dumps(record, indent=2) + "\n"
        if destination.exists():
            if destination.read_text(encoding="utf-8") != content:
                raise FileExistsError(
                    f"{destination} already exists with different contents; review the conflict manually"
                )
            staged.append(("unchanged", destination))
            continue
        destination.write_text(content, encoding="utf-8")
        staged.append(("staged", destination))
    return staged


def import_job(
    job_root: Path,
    destination_name: str,
    jobs_dir: Path,
    artifact_name: str,
    provenance: Path | None,
    replace: bool,
) -> tuple[str, Path]:
    destination = jobs_dir / destination_name
    ensure_within(destination, jobs_dir)
    source_result = job_root / "result.json"
    source_digest = sha256(source_result)

    if destination.exists():
        existing_result = destination / "result.json"
        if existing_result.is_file() and sha256(existing_result) == source_digest:
            return "unchanged", destination
        if not replace:
            raise FileExistsError(
                f"{destination} already exists with different contents; "
                "rerun with --replace only after reviewing it"
            )
        shutil.rmtree(destination)

    shutil.copytree(job_root, destination)
    if provenance and not (destination / "runner-provenance.json").exists():
        shutil.copy2(provenance, destination / "runner-provenance.json")

    manifest = {
        "schema_version": "1.0",
        "source_artifact": artifact_name,
        "imported_at": datetime.now(timezone.utc).isoformat(),
        "result_sha256": source_digest,
        "runner_provenance_included": (destination / "runner-provenance.json").is_file(),
    }
    (destination / "import-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return "imported", destination


def run_with_review(artifact: Path, jobs_dir: Path, replace: bool) -> ImportOutcome:
    artifact = artifact.resolve()
    jobs_dir = jobs_dir.resolve()
    if not artifact.exists():
        raise FileNotFoundError(f"artifact does not exist: {artifact}")

    with tempfile.TemporaryDirectory(prefix="uxl-harbor-import-") as temporary:
        if artifact.is_dir():
            reject_symlinks(artifact)
            extracted = artifact
        elif artifact.suffix.lower() == ".zip":
            extracted = Path(temporary) / "artifact"
            extracted.mkdir()
            extract_zip_safely(artifact, extracted)
        else:
            raise ValueError("artifact must be a downloaded .zip file or directory")

        roots = find_job_roots(extracted)
        if not roots:
            raise ValueError("artifact contains no Harbor job-level result.json")
        qualification_candidates = find_qualification_candidates(extracted)

        names: set[str] = set()
        entries: list[tuple[Path, str]] = []
        for root in roots:
            name = artifact.stem if root.resolve() == extracted.resolve() else root.name
            if not name or name in names:
                raise ValueError(f"artifact contains duplicate or empty job name: {name!r}")
            names.add(name)
            entries.append((root, name))

        provenance_files = sorted(extracted.rglob("runner-provenance.json"))
        shared_provenance = provenance_files[0] if len(provenance_files) == 1 else None
        jobs_dir.mkdir(parents=True, exist_ok=True)
        jobs = [
            import_job(
                root,
                name,
                jobs_dir,
                artifact.name,
                shared_provenance,
                replace,
            )
            for root, name in entries
        ]
        staged = stage_qualification_candidates(
            qualification_candidates, jobs_dir / "qualification-review"
        )
        return ImportOutcome(jobs=jobs, qualification_candidates=staged)


def run(artifact: Path, jobs_dir: Path, replace: bool) -> list[tuple[str, Path]]:
    """Import jobs while preserving the original job-only return value for callers."""
    return run_with_review(artifact, jobs_dir, replace).jobs


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path, help="Downloaded artifact .zip or extracted directory")
    parser.add_argument(
        "--jobs-dir",
        type=Path,
        default=Path("harbor-jobs"),
        help="Destination Harbor jobs directory (default: harbor-jobs)",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Replace a same-named job only when its result differs",
    )
    args = parser.parse_args(argv)
    try:
        outcome = run_with_review(args.artifact, args.jobs_dir, args.replace)
    except (FileExistsError, FileNotFoundError, OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"Artifact import failed: {exc}", file=sys.stderr)
        return 1

    for status, destination in outcome.jobs:
        print(f"{status}: {destination}")
    for status, destination in outcome.qualification_candidates:
        print(f"qualification {status} for review: {destination}")
    if outcome.qualification_candidates:
        print(
            "Review public labels and limitations, then copy the candidate into "
            "evaluation/harbor/results/qualifications/."
        )
    print("Restart the Harbor results dashboard to index imported jobs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
