"""Input validation utilities for security."""

import re
from pathlib import Path


class InvalidProjectIdError(ValueError):
    """Raised when a project_id fails validation."""
    pass


_PROJECT_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")


def validate_project_id(project_id: str) -> str:
    """
    Validate that a project_id is safe for use in file paths.

    Args:
        project_id: The project ID to validate

    Returns:
        The validated project_id (unchanged)

    Raises:
        InvalidProjectIdError: If the project_id is invalid
    """
    if not project_id or len(project_id) > 64:
        raise InvalidProjectIdError(
            f"project_id must be 1-64 characters, got {len(project_id) if project_id else 0}"
        )
    if not _PROJECT_ID_PATTERN.match(project_id):
        raise InvalidProjectIdError(
            f"project_id contains invalid characters: '{project_id}'. "
            "Only alphanumeric characters, hyphens, and underscores are allowed."
        )
    return project_id


def validate_path_within_directory(path: Path, parent_dir: Path) -> Path:
    """
    Verify that a resolved path is within the expected parent directory.

    Args:
        path: The path to check (will be resolved)
        parent_dir: The parent directory it must be within (will be resolved)

    Returns:
        The resolved path

    Raises:
        InvalidProjectIdError: If the path escapes parent_dir
    """
    resolved_path = path.resolve()
    resolved_parent = parent_dir.resolve()
    if not str(resolved_path).startswith(str(resolved_parent) + "/") and resolved_path != resolved_parent:
        raise InvalidProjectIdError(
            f"Path '{resolved_path}' is outside allowed directory '{resolved_parent}'"
        )
    return resolved_path
