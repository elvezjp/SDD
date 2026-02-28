"""Context manager for storing and retrieving interview data."""

import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from spec_ai_writer.utils.validation import (
    validate_project_id,
    validate_path_within_directory,
)


def generate_project_id() -> str:
    """Generate a unique alphanumeric project ID.

    Returns:
        An 8-character hex string (e.g., 'a1b2c3d4')
    """
    return uuid.uuid4().hex[:8]


class ContextManager:
    """Manages interview context and conversation history across phases."""

    def __init__(self, project_id: str, display_name: str = "", data_dir: str = "./data"):
        """
        Initialize the context manager.

        Args:
            project_id: Unique project identifier
            display_name: Human-readable project name
            data_dir: Root data directory for all projects
        """
        validate_project_id(project_id)
        self._project_id = project_id
        self._display_name = display_name
        self._data_dir = data_dir

        # Context structure:
        # {
        #     "project_id": str,
        #     "display_name": str,
        #     "created_at": str,
        #     "updated_at": str,
        #     "current_phase": int,
        #     "phases": {
        #         "1": {
        #             "qa_pairs": [{"question": str, "answer": str, "timestamp": str}],
        #             "structured_data": dict,
        #             "completed": bool
        #         },
        #         ...
        #     }
        # }
        self.context: Dict[str, Any] = {
            "project_id": project_id,
            "display_name": display_name,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "current_phase": 1,
            "phases": {}
        }

    @property
    def project_id(self) -> str:
        """Get the project ID."""
        return self._project_id

    @property
    def display_name(self) -> str:
        """Get the display name."""
        return self._display_name

    def get_project_dir(self) -> Path:
        """Get the project directory path."""
        project_dir = Path(self._data_dir) / self._project_id
        validate_path_within_directory(project_dir, Path(self._data_dir))
        return project_dir

    def get_specs_dir(self) -> Path:
        """Get the specs subdirectory path."""
        return self.get_project_dir() / "specs"

    @classmethod
    def create_project(cls, display_name: str, data_dir: str = "./data") -> "ContextManager":
        """
        Create a new project with auto-generated ID.

        Creates the directory structure and project.json metadata file.

        Args:
            display_name: Human-readable project name
            data_dir: Root data directory

        Returns:
            A new ContextManager instance
        """
        project_id = generate_project_id()
        instance = cls(project_id=project_id, display_name=display_name, data_dir=data_dir)

        # Create directory structure
        project_dir = instance.get_project_dir()
        project_dir.mkdir(parents=True, exist_ok=True)
        instance.get_specs_dir().mkdir(parents=True, exist_ok=True)

        # Save project.json metadata
        now = datetime.now().isoformat()
        project_metadata = {
            "project_id": project_id,
            "display_name": display_name,
            "created_at": now,
            "updated_at": now
        }
        project_json_path = project_dir / "project.json"
        with open(project_json_path, "w", encoding="utf-8") as f:
            json.dump(project_metadata, f, ensure_ascii=False, indent=2)

        # Save initial interview state
        instance.save_to_disk()

        return instance

    @classmethod
    def load_project(cls, project_id: str, data_dir: str = "./data") -> "ContextManager":
        """
        Load an existing project from disk.

        Args:
            project_id: Project identifier
            data_dir: Root data directory

        Returns:
            A ContextManager instance with loaded state

        Raises:
            FileNotFoundError: If the project directory doesn't exist
        """
        validate_project_id(project_id)
        project_dir = Path(data_dir) / project_id
        project_json_path = project_dir / "project.json"

        if not project_dir.exists():
            raise FileNotFoundError(f"Project directory not found: {project_dir}")

        # Load project metadata
        display_name = ""
        if project_json_path.exists():
            with open(project_json_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
                display_name = metadata.get("display_name", "")

        instance = cls(project_id=project_id, display_name=display_name, data_dir=data_dir)
        instance.load_from_disk()

        return instance

    @classmethod
    def list_projects(cls, data_dir: str = "./data") -> List[Dict[str, Any]]:
        """
        List all projects in the data directory.

        Args:
            data_dir: Root data directory

        Returns:
            List of project metadata dictionaries
        """
        data_path = Path(data_dir)
        if not data_path.exists():
            return []

        projects = []
        for item in sorted(data_path.iterdir()):
            if not item.is_dir():
                continue

            project_json = item / "project.json"
            if not project_json.exists():
                continue

            try:
                with open(project_json, "r", encoding="utf-8") as f:
                    metadata = json.load(f)

                # Also load interview state to get current phase
                interview_json = item / "interview.json"
                current_phase = 1
                if interview_json.exists():
                    with open(interview_json, "r", encoding="utf-8") as f:
                        interview_data = json.load(f)
                        current_phase = interview_data.get("current_phase", 1)

                projects.append({
                    "project_id": metadata.get("project_id", item.name),
                    "display_name": metadata.get("display_name", ""),
                    "created_at": metadata.get("created_at", ""),
                    "updated_at": metadata.get("updated_at", ""),
                    "current_phase": current_phase
                })
            except Exception:
                continue

        return projects

    def delete_project(self) -> None:
        """Delete the project directory and all its contents."""
        project_dir = self.get_project_dir()
        # Defense-in-depth: verify path is within data_dir before rmtree
        validate_path_within_directory(project_dir, Path(self._data_dir))
        if project_dir.exists():
            shutil.rmtree(project_dir)

    def add_qa_pair(self, phase: int, question: str, answer: str) -> None:
        """
        Add a question-answer pair to the specified phase.

        Args:
            phase: Phase number (1-7)
            question: The question asked
            answer: User's answer
        """
        phase_key = str(phase)

        if phase_key not in self.context["phases"]:
            self.context["phases"][phase_key] = {
                "qa_pairs": [],
                "structured_data": None,
                "completed": False
            }

        self.context["phases"][phase_key]["qa_pairs"].append({
            "question": question,
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        })

        self.context["updated_at"] = datetime.now().isoformat()
        self.save_to_disk()

    def get_phase_context(self, phase_num: int) -> Dict[str, Any]:
        """
        Get the context for a specific phase.

        Args:
            phase_num: Phase number (1-7)

        Returns:
            Phase context dictionary
        """
        phase_key = str(phase_num)
        return self.context["phases"].get(phase_key, {
            "qa_pairs": [],
            "structured_data": None,
            "completed": False
        })

    def get_all_context(self) -> Dict[str, Any]:
        """
        Get the complete context.

        Returns:
            Full context dictionary
        """
        return self.context.copy()

    def get_context_for_phase(self, phase_num: int) -> Dict[str, Any]:
        """
        Get context including all previous phases for the current phase.

        Args:
            phase_num: Current phase number

        Returns:
            Dictionary with current and previous phases' data
        """
        result = {
            "current_phase": phase_num,
            "current_qa": self.get_phase_context(phase_num).get("qa_pairs", []),
            "previous_phases": {}
        }

        # Include data from previous phases
        for prev_phase in range(1, phase_num):
            prev_key = str(prev_phase)
            if prev_key in self.context["phases"]:
                result["previous_phases"][prev_phase] = self.context["phases"][prev_key]

        return result

    def set_structured_data(self, phase: int, data: Dict[str, Any]) -> None:
        """
        Set structured data extracted from the phase conversation.

        Args:
            phase: Phase number
            data: Structured data dictionary
        """
        phase_key = str(phase)

        if phase_key not in self.context["phases"]:
            self.context["phases"][phase_key] = {
                "qa_pairs": [],
                "structured_data": None,
                "completed": False
            }

        self.context["phases"][phase_key]["structured_data"] = data
        self.context["updated_at"] = datetime.now().isoformat()
        self.save_to_disk()

    def get_structured_data(self, phase: int) -> Optional[Dict[str, Any]]:
        """
        Get structured data for a phase.

        Args:
            phase: Phase number

        Returns:
            Structured data dictionary or None
        """
        phase_key = str(phase)
        phase_data = self.context["phases"].get(phase_key, {})
        return phase_data.get("structured_data")

    def mark_phase_complete(self, phase: int) -> None:
        """
        Mark a phase as completed.

        Args:
            phase: Phase number to mark complete
        """
        phase_key = str(phase)

        if phase_key not in self.context["phases"]:
            self.context["phases"][phase_key] = {
                "qa_pairs": [],
                "structured_data": None,
                "completed": False
            }

        self.context["phases"][phase_key]["completed"] = True
        self.context["current_phase"] = phase + 1
        self.context["updated_at"] = datetime.now().isoformat()
        self.save_to_disk()

    def is_phase_complete(self, phase: int) -> bool:
        """
        Check if a phase is completed.

        Args:
            phase: Phase number

        Returns:
            True if phase is complete
        """
        phase_key = str(phase)
        phase_data = self.context["phases"].get(phase_key, {})
        return phase_data.get("completed", False)

    def get_conversation_history(self, phase: int) -> str:
        """
        Get formatted conversation history for a phase.

        Args:
            phase: Phase number

        Returns:
            Formatted conversation history string
        """
        phase_data = self.get_phase_context(phase)
        qa_pairs = phase_data.get("qa_pairs", [])

        if not qa_pairs:
            return ""

        lines = []
        for i, qa in enumerate(qa_pairs, 1):
            lines.append(f"Q{i}: {qa['question']}")
            lines.append(f"A{i}: <user_answer>{qa['answer']}</user_answer>")
            lines.append("")

        return "\n".join(lines)

    def get_current_phase(self) -> int:
        """
        Get the current phase number.

        Returns:
            Current phase number
        """
        return self.context.get("current_phase", 1)

    def save_to_disk(self) -> None:
        """Save context to disk as interview.json in the project directory."""
        project_dir = self.get_project_dir()
        project_dir.mkdir(parents=True, exist_ok=True)
        file_path = project_dir / "interview.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.context, f, ensure_ascii=False, indent=2)

        # Also update project.json updated_at
        project_json_path = project_dir / "project.json"
        if project_json_path.exists():
            try:
                with open(project_json_path, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                metadata["updated_at"] = datetime.now().isoformat()
                with open(project_json_path, "w", encoding="utf-8") as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
            except Exception:
                pass

    def load_from_disk(self) -> None:
        """Load context from disk if it exists."""
        file_path = self.get_project_dir() / "interview.json"

        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    loaded_context = json.load(f)
                    self.context.update(loaded_context)
                    # Update display_name from loaded data if available
                    if loaded_context.get("display_name"):
                        self._display_name = loaded_context["display_name"]
            except Exception as e:
                # If loading fails, keep the default context
                print(f"Warning: Could not load context from {file_path}: {e}")

    def reset_phase(self, phase: int) -> None:
        """
        Reset a specific phase (useful for retrying).

        Args:
            phase: Phase number to reset
        """
        phase_key = str(phase)
        if phase_key in self.context["phases"]:
            self.context["phases"][phase_key] = {
                "qa_pairs": [],
                "structured_data": None,
                "completed": False
            }
            self.context["updated_at"] = datetime.now().isoformat()
            self.save_to_disk()

    def extract_structured_data(
        self,
        phase_num: int,
        llm_client: Any,
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract structured data from conversation using LLM.

        Args:
            phase_num: Phase number
            llm_client: LLM client instance
            schema: Expected data schema

        Returns:
            Extracted structured data
        """
        conversation = self.get_conversation_history(phase_num)

        if not conversation:
            return {}

        structured_data = llm_client.extract_structured_data(conversation, schema)
        self.set_structured_data(phase_num, structured_data)

        return structured_data
