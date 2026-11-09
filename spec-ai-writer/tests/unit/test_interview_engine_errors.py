"""
Unit tests for how InterviewEngine handles LLM failures (Issue #97).

When the LLM call fails, the engine must raise instead of returning a canned
question or treating the phase as incomplete.
"""

from unittest.mock import AsyncMock

import pytest

from spec_ai_writer.core.interview_engine import InterviewEngine
from spec_ai_writer.core.phase_manager import PhaseManager
from spec_ai_writer.llm.base import BaseLLMClient
from spec_ai_writer.llm.exceptions import (
    LLMAuthenticationError,
    LLMConnectionError,
    LLMResponseError,
)


@pytest.fixture
def llm() -> AsyncMock:
    return AsyncMock(spec=BaseLLMClient)


@pytest.fixture
def engine(llm, context_manager) -> InterviewEngine:
    return InterviewEngine(llm, PhaseManager(), context_manager)


def _add_qa_pairs(context_manager, phase: int, count: int) -> None:
    for i in range(count):
        context_manager.add_qa_pair(phase, f"質問{i}", f"回答{i}")


@pytest.mark.unit
class TestQuestionGenerationFailure:
    """A failed or empty LLM response is raised, not replaced by a canned question."""

    @pytest.mark.parametrize(
        "error",
        [
            LLMResponseError("Claude API error: 400"),
            LLMAuthenticationError("invalid key"),
            LLMConnectionError("timeout"),
        ],
    )
    async def test_initial_question_raises(self, engine, llm, error):
        llm.generate_question.side_effect = error

        with pytest.raises(type(error)):
            await engine._generate_initial_question(1)

    @pytest.mark.parametrize(
        "error",
        [
            LLMResponseError("Claude API error: 400"),
            LLMAuthenticationError("invalid key"),
            LLMConnectionError("timeout"),
        ],
    )
    async def test_follow_up_question_raises(self, engine, llm, context_manager, error):
        llm.generate_question.side_effect = error

        with pytest.raises(type(error)):
            await engine._generate_follow_up_question(1, context_manager)

    @pytest.mark.parametrize("empty", ["", "   \n", None])
    async def test_empty_initial_question_raises(self, engine, llm, empty):
        llm.generate_question.return_value = empty

        with pytest.raises(LLMResponseError, match="応答が空"):
            await engine._generate_initial_question(1)

    @pytest.mark.parametrize("empty", ["", "   \n", None])
    async def test_empty_follow_up_question_raises(self, engine, llm, context_manager, empty):
        llm.generate_question.return_value = empty

        with pytest.raises(LLMResponseError, match="応答が空"):
            await engine._generate_follow_up_question(1, context_manager)

    async def test_question_is_stripped(self, engine, llm, context_manager):
        llm.generate_question.return_value = "  プロジェクトの目的は何ですか？\n"

        assert await engine._generate_initial_question(1) == "プロジェクトの目的は何ですか？"
        assert (
            await engine._generate_follow_up_question(1, context_manager)
            == "プロジェクトの目的は何ですか？"
        )


@pytest.mark.unit
class TestPhaseCompletionFailure:
    """A failed completion check is raised, not reported as "not complete"."""

    async def test_llm_error_is_raised(self, engine, llm, context_manager):
        _add_qa_pairs(context_manager, 1, 3)
        llm.extract_structured_data.side_effect = LLMResponseError("Claude API error: 400")

        with pytest.raises(LLMResponseError):
            await engine._is_phase_complete(1, context_manager)

    async def test_fewer_than_three_answers_is_incomplete_without_llm(
        self, engine, llm, context_manager
    ):
        _add_qa_pairs(context_manager, 1, 2)

        assert await engine._is_phase_complete(1, context_manager) is False
        llm.extract_structured_data.assert_not_called()

    async def test_empty_extraction_is_still_incomplete(self, engine, llm, context_manager):
        _add_qa_pairs(context_manager, 1, 3)
        llm.extract_structured_data.return_value = {}

        assert await engine._is_phase_complete(1, context_manager) is False


@pytest.mark.unit
class TestUndoLastQaPair:
    def test_removes_answer_and_restores_pending_question(self, context_manager):
        context_manager.add_qa_pair(1, "質問A", "回答A")
        context_manager.set_pending_question(1, "質問B")
        context_manager.add_qa_pair(1, "質問B", "回答B")

        context_manager.undo_last_qa_pair(1, "質問B")

        phase = context_manager.get_phase_context(1)
        assert [qa["answer"] for qa in phase["qa_pairs"]] == ["回答A"]
        assert context_manager.get_pending_question(1) == "質問B"

    def test_does_nothing_without_answers(self, context_manager):
        context_manager.undo_last_qa_pair(1, "質問A")

        assert context_manager.get_phase_context(1).get("qa_pairs", []) == []
