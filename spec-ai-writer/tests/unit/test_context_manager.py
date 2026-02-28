"""
Unit tests for ContextManager
"""

import pytest
import json
from pathlib import Path

from spec_ai_writer.core.context_manager import ContextManager
from spec_ai_writer.utils.validation import InvalidProjectIdError


@pytest.mark.unit
class TestContextManager:
    """Test ContextManager functionality."""

    def test_initialization(self, temp_dir):
        """Test context manager initialization."""
        data_dir = str(temp_dir / "data")
        manager = ContextManager("proj001", display_name="test-project", data_dir=data_dir)
        assert manager.project_id == "proj001"
        assert manager.display_name == "test-project"
        # Context now includes metadata fields
        assert "project_id" in manager.context
        assert "display_name" in manager.context
        assert "created_at" in manager.context
        assert "updated_at" in manager.context
        assert "current_phase" in manager.context
        assert "phases" in manager.context
        assert manager.context["project_id"] == "proj001"
        assert manager.context["display_name"] == "test-project"
        assert manager.context["current_phase"] == 1
        assert manager.context["phases"] == {}

    def test_add_qa_pair(self, context_manager):
        """Test adding Q&A pairs."""
        phase_num = 1
        question = "プロジェクトの目的は？"
        answer = "Webアプリ開発"

        context_manager.add_qa_pair(phase_num, question, answer)

        phase_context = context_manager.get_phase_context(phase_num)
        assert "qa_pairs" in phase_context
        assert len(phase_context["qa_pairs"]) == 1
        assert phase_context["qa_pairs"][0]["question"] == question
        assert phase_context["qa_pairs"][0]["answer"] == answer

    def test_add_multiple_qa_pairs(self, context_manager, sample_qa_pairs):
        """Test adding multiple Q&A pairs."""
        phase_num = 1

        for qa in sample_qa_pairs:
            context_manager.add_qa_pair(phase_num, qa["question"], qa["answer"])

        phase_context = context_manager.get_phase_context(phase_num)
        assert len(phase_context["qa_pairs"]) == len(sample_qa_pairs)

    def test_get_phase_context_empty(self, temp_dir):
        """Test getting context for phase with no data."""
        data_dir = str(temp_dir / "data" / "empty")
        manager = ContextManager("emptyproj", display_name="empty", data_dir=data_dir)
        phase_context = manager.get_phase_context(1)
        # get_phase_context now returns default structure if phase doesn't exist
        assert "qa_pairs" in phase_context
        assert phase_context["qa_pairs"] == []
        assert phase_context["structured_data"] is None
        assert phase_context["completed"] is False

    def test_get_phase_context_with_data(self, context_manager):
        """Test getting context after adding data."""
        phase_num = 1
        context_manager.add_qa_pair(phase_num, "Q1", "A1")
        context_manager.add_qa_pair(phase_num, "Q2", "A2")

        phase_context = context_manager.get_phase_context(phase_num)
        assert "qa_pairs" in phase_context
        assert len(phase_context["qa_pairs"]) == 2

    def test_get_context_for_phase(self, temp_dir):
        """Test getting context including previous phases."""
        data_dir = str(temp_dir / "data" / "context_for_phase")
        manager = ContextManager("ctxproj", display_name="context-test", data_dir=data_dir)
        manager.get_project_dir().mkdir(parents=True, exist_ok=True)

        # Add data to phase 1
        manager.add_qa_pair(1, "Phase 1 Q", "Phase 1 A")
        # Add data to phase 2
        manager.add_qa_pair(2, "Phase 2 Q", "Phase 2 A")

        # Get context for phase 2 (should include phase 1 in previous_phases)
        context = manager.get_context_for_phase(2)
        assert "current_phase" in context
        assert context["current_phase"] == 2
        assert "current_qa" in context
        assert "previous_phases" in context
        assert 1 in context["previous_phases"]
        assert len(context["previous_phases"][1]["qa_pairs"]) == 1
        assert len(context["current_qa"]) == 1

    def test_save_and_load(self, sample_qa_pairs, temp_dir):
        """Test saving and loading context."""
        data_dir = str(temp_dir / "data")
        manager = ContextManager.create_project(display_name="save-test", data_dir=data_dir)
        project_id = manager.project_id

        # Add data
        for qa in sample_qa_pairs:
            manager.add_qa_pair(1, qa["question"], qa["answer"])

        # save_to_disk is called automatically in add_qa_pair
        # Verify file exists
        interview_file = manager.get_project_dir() / "interview.json"
        assert interview_file.exists()

        # Load into new manager
        new_manager = ContextManager.load_project(project_id, data_dir=data_dir)

        # Verify data
        phase_context = new_manager.get_phase_context(1)
        assert len(phase_context["qa_pairs"]) == len(sample_qa_pairs)

    def test_extract_structured_data(self, temp_dir, mock_llm_client):
        """Test extracting structured data from conversation."""
        data_dir = str(temp_dir / "data" / "extract")
        manager = ContextManager("extractproj", display_name="extract-test", data_dir=data_dir)
        manager.get_project_dir().mkdir(parents=True, exist_ok=True)

        # Add sample Q&A pairs
        manager.add_qa_pair(1, "目的は？", "Webアプリ開発")
        manager.add_qa_pair(1, "背景は？", "既存システムの老朽化")

        # Extract data - note: signature is (phase_num, llm_client, schema)
        schema = {
            "project_name": "プロジェクト名",
            "background": "背景",
            "purposes": "目的"
        }

        data = manager.extract_structured_data(1, mock_llm_client, schema)

        # Verify LLM was called
        assert mock_llm_client.extract_structured_data.called
        assert "project_name" in data
        assert "background" in data

    def test_json_serialization(self, temp_dir):
        """Test JSON serialization/deserialization."""
        data_dir = str(temp_dir / "data" / "serial")
        manager = ContextManager("serialproj", display_name="serial-test", data_dir=data_dir)
        manager.get_project_dir().mkdir(parents=True, exist_ok=True)

        # Add complex data
        manager.add_qa_pair(1, "Question", "Answer")
        # Access phases with string key (as that's how they're stored)
        manager.context["phases"]["1"]["metadata"] = {
            "nested": {"key": "value"},
            "list": [1, 2, 3]
        }
        manager.save_to_disk()

        # Verify JSON is valid
        interview_file = manager.get_project_dir() / "interview.json"
        with open(interview_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)

        assert "phases" in loaded_data
        assert "1" in loaded_data["phases"]
        assert loaded_data["phases"]["1"]["metadata"]["nested"]["key"] == "value"

    def test_create_project(self, temp_dir):
        """Test creating a project with auto-generated ID."""
        data_dir = str(temp_dir / "data")
        manager = ContextManager.create_project(display_name="new-project", data_dir=data_dir)

        assert manager.project_id  # Should be non-empty
        assert len(manager.project_id) == 8  # 8-char hex string
        assert manager.display_name == "new-project"
        assert manager.get_project_dir().exists()
        assert manager.get_specs_dir().exists()
        assert (manager.get_project_dir() / "project.json").exists()
        assert (manager.get_project_dir() / "interview.json").exists()

    def test_list_projects(self, temp_dir):
        """Test listing projects."""
        data_dir = str(temp_dir / "data")

        # Create multiple projects
        m1 = ContextManager.create_project(display_name="project-1", data_dir=data_dir)
        m2 = ContextManager.create_project(display_name="project-2", data_dir=data_dir)

        projects = ContextManager.list_projects(data_dir=data_dir)
        assert len(projects) == 2

        display_names = {p["display_name"] for p in projects}
        assert "project-1" in display_names
        assert "project-2" in display_names

    def test_delete_project(self, temp_dir):
        """Test deleting a project."""
        data_dir = str(temp_dir / "data")
        manager = ContextManager.create_project(display_name="to-delete", data_dir=data_dir)
        project_dir = manager.get_project_dir()

        assert project_dir.exists()
        manager.delete_project()
        assert not project_dir.exists()

    def test_rejects_path_traversal_project_id(self, temp_dir):
        """Test that path traversal in project_id is rejected."""
        data_dir = str(temp_dir / "data")
        with pytest.raises(InvalidProjectIdError):
            ContextManager("../../etc/passwd", data_dir=data_dir)

    def test_rejects_slash_in_project_id(self, temp_dir):
        """Test that slashes in project_id are rejected."""
        data_dir = str(temp_dir / "data")
        with pytest.raises(InvalidProjectIdError):
            ContextManager("foo/bar", data_dir=data_dir)

    def test_rejects_dots_in_project_id(self, temp_dir):
        """Test that dots in project_id are rejected."""
        data_dir = str(temp_dir / "data")
        with pytest.raises(InvalidProjectIdError):
            ContextManager("..", data_dir=data_dir)

    def test_load_project_rejects_traversal(self, temp_dir):
        """Test that load_project rejects path traversal."""
        data_dir = str(temp_dir / "data")
        with pytest.raises(InvalidProjectIdError):
            ContextManager.load_project("../../etc", data_dir=data_dir)
