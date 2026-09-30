"""Validation and path construction for DVC proof jobs."""

from pathlib import Path
import re


REQUEST_ID_PATTERN = re.compile(r"[A-Za-z0-9_-]{1,64}")


def validate_request_id(value: object) -> str:
    """Return a filesystem-safe client job ID or raise ValueError."""
    if not isinstance(value, str) or not REQUEST_ID_PATTERN.fullmatch(value):
        raise ValueError(
            "requestid must contain 1-64 letters, numbers, underscores, or hyphens"
        )
    return value


def build_job_paths(request_id: str, root: Path) -> tuple[Path, Path]:
    """Build input and output paths and ensure they stay under their roots."""
    safe_request_id = validate_request_id(request_id)
    resolved_root = root.resolve()
    input_root = resolved_root / "request_data"
    output_root = resolved_root / "proof_output"
    input_path = (input_root / f"{safe_request_id}.json").resolve()
    output_path = (output_root / safe_request_id).resolve()

    if input_root not in input_path.parents or output_root not in output_path.parents:
        raise ValueError("requestid resolves outside the job storage directories")

    return input_path, output_path
