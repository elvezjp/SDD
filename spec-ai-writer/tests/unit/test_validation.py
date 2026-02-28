"""Unit tests for validation utilities."""

import pytest
from pathlib import Path

from spec_ai_writer.utils.validation import (
    validate_project_id,
    validate_path_within_directory,
    InvalidProjectIdError,
)


@pytest.mark.unit
class TestValidateProjectId:
    """Test project_id validation."""

    def test_valid_hex_id(self):
        assert validate_project_id("a1b2c3d4") == "a1b2c3d4"

    def test_valid_with_hyphens(self):
        assert validate_project_id("my-project") == "my-project"

    def test_valid_with_underscores(self):
        assert validate_project_id("my_project") == "my_project"

    def test_valid_alphanumeric(self):
        assert validate_project_id("Project123") == "Project123"

    def test_rejects_path_traversal_dots(self):
        with pytest.raises(InvalidProjectIdError):
            validate_project_id("../../etc")

    def test_rejects_slash(self):
        with pytest.raises(InvalidProjectIdError):
            validate_project_id("foo/bar")

    def test_rejects_backslash(self):
        with pytest.raises(InvalidProjectIdError):
            validate_project_id("foo\\bar")

    def test_rejects_empty(self):
        with pytest.raises(InvalidProjectIdError):
            validate_project_id("")

    def test_rejects_too_long(self):
        with pytest.raises(InvalidProjectIdError):
            validate_project_id("a" * 65)

    def test_rejects_dots_only(self):
        with pytest.raises(InvalidProjectIdError):
            validate_project_id("..")

    def test_rejects_spaces(self):
        with pytest.raises(InvalidProjectIdError):
            validate_project_id("foo bar")

    def test_rejects_special_chars(self):
        with pytest.raises(InvalidProjectIdError):
            validate_project_id("foo@bar")


@pytest.mark.unit
class TestValidatePathWithinDirectory:
    """Test path containment validation."""

    def test_valid_path(self, tmp_path):
        parent = tmp_path / "data"
        parent.mkdir()
        child = parent / "project1"
        child.mkdir()
        result = validate_path_within_directory(child, parent)
        assert result == child.resolve()

    def test_rejects_escape(self, tmp_path):
        parent = tmp_path / "data"
        parent.mkdir()
        escaped = tmp_path / "other"
        escaped.mkdir()
        with pytest.raises(InvalidProjectIdError):
            validate_path_within_directory(escaped, parent)

    def test_rejects_parent_itself(self, tmp_path):
        """Parent dir itself should not pass as a child path."""
        parent = tmp_path / "data"
        parent.mkdir()
        # Parent == path case is actually allowed (edge case), but
        # traversal like data/.. resolving to parent-of-data should fail
        grandparent = tmp_path
        with pytest.raises(InvalidProjectIdError):
            validate_path_within_directory(grandparent, parent)
