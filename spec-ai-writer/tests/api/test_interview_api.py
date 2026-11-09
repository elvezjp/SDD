"""
API tests for how POST /api/interview/answer handles LLM failures (Issue #97).
"""

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from spec_ai_writer.config.settings import get_settings
from spec_ai_writer.core.context_manager import ContextManager
from spec_ai_writer.core.phase_manager import PhaseManager
from spec_ai_writer.llm.base import BaseLLMClient
from spec_ai_writer.llm.exceptions import (
    LLMAuthenticationError,
    LLMConnectionError,
    LLMResponseError,
)

LLM_ERROR = "Claude API error: `temperature` is deprecated for this model."


@pytest.fixture
def llm(monkeypatch) -> AsyncMock:
    """Replace the LLM client that the interview router creates."""
    client = AsyncMock(spec=BaseLLMClient)
    monkeypatch.setattr(
        "spec_ai_writer.web.routers.interview.LLMFactory.create_client",
        lambda *args, **kwargs: client,
    )
    return client


@pytest.fixture
def project_id(test_client: TestClient) -> str:
    response = test_client.post("/api/projects/", json={"display_name": "test-project"})
    assert response.status_code == 201
    return response.json()["project_id"]


def _load(project_id: str) -> ContextManager:
    return ContextManager.load_project(project_id, data_dir=get_settings().data_dir)


def _answer(test_client: TestClient, project_id: str, answer=None):
    body = {"project_id": project_id}
    if answer is not None:
        body["answer"] = answer
    return test_client.post("/api/interview/answer", json=body)


@pytest.mark.api
class TestAnswerLLMFailure:
    def test_failed_first_question_returns_502_with_cause(self, test_client, llm, project_id):
        llm.generate_question.side_effect = LLMResponseError(LLM_ERROR)

        response = _answer(test_client, project_id)

        assert response.status_code == 502
        assert "LLM から応答を受け取れませんでした" in response.json()["detail"]
        assert LLM_ERROR in response.json()["detail"]
        assert _load(project_id).get_pending_question(1) is None

    def test_failed_follow_up_question_does_not_keep_the_answer(self, test_client, llm, project_id):
        llm.generate_question.return_value = "最初の質問"
        assert _answer(test_client, project_id).status_code == 200

        llm.generate_question.return_value = None
        llm.generate_question.side_effect = LLMResponseError(LLM_ERROR)
        response = _answer(test_client, project_id, "最初の回答")

        assert response.status_code == 502
        context = _load(project_id)
        assert context.get_phase_context(1)["qa_pairs"] == []
        assert context.get_pending_question(1) == "最初の質問"

        # Sending the same answer again saves it once
        llm.generate_question.side_effect = None
        llm.generate_question.return_value = "次の質問"
        response = _answer(test_client, project_id, "最初の回答")

        assert response.status_code == 200
        assert response.json()["question"] == "次の質問"
        qa_pairs = _load(project_id).get_phase_context(1)["qa_pairs"]
        assert [(qa["question"], qa["answer"]) for qa in qa_pairs] == [("最初の質問", "最初の回答")]

    def test_failed_completion_check_does_not_keep_the_answer(self, test_client, llm, project_id):
        context = _load(project_id)
        for i in range(2):
            context.add_qa_pair(1, f"質問{i}", f"回答{i}")
        context.set_pending_question(1, "3つ目の質問")

        llm.extract_structured_data.side_effect = LLMResponseError(LLM_ERROR)
        response = _answer(test_client, project_id, "3つ目の回答")

        assert response.status_code == 502
        context = _load(project_id)
        assert len(context.get_phase_context(1)["qa_pairs"]) == 2
        assert context.get_pending_question(1) == "3つ目の質問"
        assert not context.is_phase_complete(1)

    def test_answer_without_pending_question_is_rejected(self, test_client, llm, project_id):
        response = _answer(test_client, project_id, "質問が無いのに送った回答")

        assert response.status_code == 409
        assert "ページを再読み込み" in response.json()["detail"]
        assert _load(project_id).get_phase_context(1).get("qa_pairs", []) == []


@pytest.mark.api
class TestAnswerLLMErrorStatus:
    """LLM errors reach their handlers through the disconnect guard."""

    @pytest.mark.parametrize(
        "error, status_code",
        [
            (LLMAuthenticationError("invalid key"), 401),
            (LLMConnectionError("timeout"), 502),
            (LLMResponseError(LLM_ERROR), 502),
        ],
    )
    def test_status_code(self, test_client, llm, project_id, error, status_code):
        llm.generate_question.side_effect = error

        assert _answer(test_client, project_id).status_code == status_code


@pytest.mark.api
class TestAnswerPhaseCompletion:
    def test_completing_a_phase_returns_the_next_question(
        self, test_client, llm, project_id, monkeypatch
    ):
        """Regression test for Issue #109: phase completion was reported as a disconnect."""
        monkeypatch.setattr(get_settings(), "auto_git_commit", False)
        llm.generate_question.return_value = "次の質問です"
        llm.extract_structured_data.return_value = {
            field: ["value"] for field in PhaseManager().get_required_fields(1)
        }

        assert _answer(test_client, project_id).status_code == 200
        for number in range(1, 3):
            assert _answer(test_client, project_id, f"回答{number}").status_code == 200
        response = _answer(test_client, project_id, "回答3")

        assert response.status_code == 200
        body = response.json()
        assert body["phase_complete"] is True
        assert body["phase_num"] == 1
        assert body["question"] == "次の質問です"
        context = _load(project_id)
        assert context.is_phase_complete(1)
        assert context.get_pending_question(2) == "次の質問です"
