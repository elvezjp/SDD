import pytest

from spec_ai_writer.core.interview_engine import InterviewEngine
from spec_ai_writer.llm.exceptions import LLMResponseError


class FailingLLM:
    async def generate_question(self, *_args, **_kwargs):
        raise RuntimeError("provider returned an invalid response")


def make_engine(data_dir):
    from spec_ai_writer.core.context_manager import ContextManager
    from spec_ai_writer.core.phase_manager import PhaseManager

    return InterviewEngine(
        FailingLLM(), PhaseManager(), ContextManager("deadbeef", data_dir=str(data_dir))
    )


@pytest.mark.asyncio
async def test_initial_question_failure_is_not_replaced_with_template(tmp_path, monkeypatch):
    engine = make_engine(tmp_path)

    with pytest.raises(LLMResponseError, match="初回質問を生成できませんでした"):
        await engine._generate_initial_question(1)


@pytest.mark.asyncio
async def test_follow_up_question_failure_is_not_replaced_with_template(tmp_path, monkeypatch):
    engine = make_engine(tmp_path)

    with pytest.raises(LLMResponseError, match="フォローアップ質問を生成できませんでした"):
        await engine._generate_follow_up_question(1, engine.context_mgr)
