"""Interview engine for conducting SDD interviews."""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from spec_ai_writer.config.prompts import PHASE_SYSTEM_PROMPTS
from spec_ai_writer.core.context_manager import ContextManager
from spec_ai_writer.core.phase_manager import PhaseManager
from spec_ai_writer.llm.base import BaseLLMClient
from spec_ai_writer.llm.exceptions import (
    LLMAuthenticationError,
    LLMConnectionError,
    LLMResponseError,
)

logger = logging.getLogger(__name__)


class InterviewEngine:
    """Orchestrates the interview process for all 7 phases."""

    def __init__(
        self,
        llm_client: BaseLLMClient,
        phase_manager: PhaseManager,
        context_manager: ContextManager
    ):
        """
        Initialize the interview engine.

        Args:
            llm_client: LLM client for generating questions
            phase_manager: Phase manager for workflow control
            context_manager: Context manager for storing conversation
        """
        self.llm = llm_client
        self.phase_mgr = phase_manager
        self.context_mgr = context_manager

    async def start_interview(self) -> None:
        """Start the interview from the current phase."""
        current_phase = self.context_mgr.get_current_phase()

        print(f"\n{'='*60}")
        print(f"仕様駆動開発（SDD）インタビューを開始します")
        print(f"プロジェクト: {self.context_mgr.project_id}")
        print(f"現在のフェーズ: {current_phase}")
        print(f"{'='*60}\n")

        # Conduct interviews for each phase from current to phase 7
        for phase_num in range(current_phase, 8):
            if not await self._conduct_phase_interview(phase_num):
                # User requested to stop
                print("\nインタビューを中断しました。")
                print(f"次回は 'spec resume {self.context_mgr.project_id}' で再開できます。")
                return

        print("\n" + "="*60)
        print("すべてのフェーズが完了しました！おめでとうございます！")
        print("="*60 + "\n")

    async def _conduct_phase_interview(self, phase_num: int) -> bool:
        """
        Conduct interview for a specific phase.

        Args:
            phase_num: Phase number (1-7)

        Returns:
            True if phase completed, False if user wants to stop
        """
        phase_info = self.phase_mgr.get_phase_info(phase_num)

        print(f"\n{'─'*60}")
        print(f"フェーズ {phase_num}: {phase_info.name}")
        print(f"{phase_info.description}")
        print(f"{'─'*60}\n")

        # Show initial prompt
        initial_prompt = self.phase_mgr.get_initial_prompt(phase_num)
        print(initial_prompt)
        print()

        # Get system prompt for this phase
        system_prompt = self._get_system_prompt_for_phase(phase_num)

        # Question-answer loop
        qa_count = 0
        max_questions = 15  # Safety limit

        while qa_count < max_questions:
            # Generate next question
            context = self._build_context_for_question(phase_num)
            question = await self._generate_next_question(system_prompt, context)

            if not question or question.strip() == "":
                break

            # Ask the question
            print(f"\n質問: {question}")
            print("回答: ", end="", flush=True)

            try:
                answer = input().strip()
            except (KeyboardInterrupt, EOFError):
                print("\n\nインタビューを中断しますか？ (y/n): ", end="", flush=True)
                try:
                    response = input().strip().lower()
                    if response in ['y', 'yes', 'はい']:
                        return False
                except (KeyboardInterrupt, EOFError):
                    return False

            if not answer:
                print("回答が空です。もう一度入力してください。")
                continue

            # Check for exit commands
            if answer.lower() in ['exit', 'quit', '終了', '中断']:
                print("\nインタビューを中断しますか？ (y/n): ", end="", flush=True)
                response = input().strip().lower()
                if response in ['y', 'yes', 'はい']:
                    return False
                continue

            # Save Q&A pair
            self.context_mgr.add_qa_pair(phase_num, question, answer)
            qa_count += 1

            # Check if we have enough information
            if qa_count >= 3:  # After at least 3 Q&A pairs (per SPEC.md 3.3)
                if await self._check_phase_completion(phase_num):
                    break

        # Extract structured data and generate spec
        print("\n情報を整理しています...")
        await self._generate_and_save_spec(phase_num)

        print(f"\nフェーズ {phase_num} が完了しました！")

        return True

    async def _generate_next_question(
        self,
        system_prompt: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Generate the next question using LLM.

        Args:
            system_prompt: System prompt for the phase
            context: Current context

        Returns:
            Generated question
        """
        try:
            question = await self.llm.generate_question(system_prompt, context)
            return question.strip()
        except LLMAuthenticationError as e:
            logger.error(f"LLM認証エラー: {e}")
            print(f"\nエラー: APIキーが無効です。.env ファイルの設定を確認してください。")
            return ""
        except LLMConnectionError as e:
            logger.error(f"LLM接続エラー: {e}")
            print(f"\nエラー: LLMサービスに接続できません。ネットワーク接続を確認してください。")
            return ""
        except (LLMResponseError, Exception) as e:
            logger.error(f"質問生成エラー: {e}")
            print(f"\n質問の生成中にエラーが発生しました: {e}")
            return ""

    def _build_context_for_question(self, phase_num: int) -> Dict[str, Any]:
        """
        Build context for question generation.

        Args:
            phase_num: Current phase number

        Returns:
            Context dictionary
        """
        conversation_history = self.context_mgr.get_conversation_history(phase_num)
        required_fields = self.phase_mgr.get_required_fields(phase_num)

        # Determine which fields still need information
        phase_data = self.context_mgr.get_phase_context(phase_num)
        structured_data = phase_data.get("structured_data", {}) or {}
        missing_fields = [f for f in required_fields if f not in structured_data or not structured_data[f]]

        # Load previous phase specifications
        previous_phases = self._load_previous_phase_specs(phase_num)

        return {
            "conversation_history": conversation_history,
            "missing_fields": missing_fields,
            "qa_count": len(phase_data.get("qa_pairs", [])),
            "previous_phases": previous_phases
        }

    async def _check_phase_completion(self, phase_num: int) -> bool:
        """
        Check if phase has enough information to complete.

        Args:
            phase_num: Phase number

        Returns:
            True if phase can be completed
        """
        # Try to extract structured data
        conversation = self.context_mgr.get_conversation_history(phase_num)
        if not conversation:
            return False

        try:
            schema = self.phase_mgr.get_schema_for_phase(phase_num)
            structured_data = await self.llm.extract_structured_data(conversation, schema)

            # Check if extraction returned empty result
            if not structured_data:
                logger.info(f"フェーズ{phase_num}: 構造化データの抽出結果が空です")
                return False

            # Validate completeness
            is_valid, missing = self.phase_mgr.validate_phase_completion(
                phase_num,
                structured_data
            )

            if is_valid:
                # 完了判定と同時に保存することで _extract_and_save_structured_data の再抽出を省く
                self.context_mgr.set_structured_data(phase_num, structured_data)

            return is_valid
        except Exception as e:
            # 「未完了」として返すと、何度答えてもフェーズが終わらない（Issue #97）
            logger.error(f"フェーズ{phase_num}の完了判定に失敗: {e}")
            raise

    async def _extract_and_save_structured_data(self, phase_num: int) -> bool:
        """
        Extract structured data from conversation and save it.

        Args:
            phase_num: Phase number

        Returns:
            True if extraction succeeded with non-empty data, False otherwise
        """
        try:
            # _check_phase_completion が完了判定時に保存済みの場合はスキップ
            if self.context_mgr.get_structured_data(phase_num):
                return True

            schema = self.phase_mgr.get_schema_for_phase(phase_num)
            structured_data = await self.context_mgr.extract_structured_data(
                phase_num,
                self.llm,
                schema
            )

            non_null_count = sum(1 for v in structured_data.values() if v is not None)

            if non_null_count == 0:
                logger.warning(f"フェーズ{phase_num}: 構造化データの抽出に失敗しました。リトライします...")
                # 1回リトライ
                structured_data = await self.context_mgr.extract_structured_data(
                    phase_num,
                    self.llm,
                    schema
                )
                non_null_count = sum(1 for v in structured_data.values() if v is not None)

            if non_null_count == 0:
                print("警告: 構造化データの抽出に失敗しました。インタビュー内容を見直してください。")
                return False

            print(f"データを抽出しました（有効項目: {non_null_count}/{len(structured_data)}）")
            return True
        except LLMAuthenticationError as e:
            logger.error(f"LLM認証エラー: {e}")
            print(f"エラー: APIキーが無効です。.env ファイルの設定を確認してください。")
            return False
        except LLMConnectionError as e:
            logger.error(f"LLM接続エラー: {e}")
            print(f"エラー: LLMサービスに接続できません。ネットワーク接続を確認してください。")
            return False
        except (LLMResponseError, Exception) as e:
            logger.error(f"データ抽出中にエラー: {e}")
            print(f"データ抽出中にエラーが発生しました: {e}")
            return False

    def _get_system_prompt_for_phase(self, phase_num: int) -> str:
        """
        Get system prompt for a specific phase.

        Args:
            phase_num: Phase number

        Returns:
            System prompt string
        """
        if phase_num in PHASE_SYSTEM_PROMPTS:
            return PHASE_SYSTEM_PROMPTS[phase_num]
        phase_info = self.phase_mgr.get_phase_info(phase_num)
        return f"""あなたは仕様駆動開発の専門家です。
現在、フェーズ {phase_num}: {phase_info.name} を担当しています。

{phase_info.description}

ユーザーに質問をして、必要な情報を収集してください。
一度に1つの質問をし、ユーザーの回答に基づいて適切なフォローアップをしてください。"""

    async def resume_interview(self) -> None:
        """Resume a previously interrupted interview."""
        current_phase = self.context_mgr.get_current_phase()

        print(f"\n{'='*60}")
        print(f"インタビューを再開します")
        print(f"プロジェクト: {self.context_mgr.project_id}")
        print(f"現在のフェーズ: {current_phase}")
        print(f"{'='*60}\n")

        # Show what was collected so far
        phase_data = self.context_mgr.get_phase_context(current_phase)
        qa_pairs = phase_data.get("qa_pairs", [])

        if qa_pairs:
            print(f"これまでに {len(qa_pairs)} 個の質問に答えています。\n")

        # Continue from current phase
        await self.start_interview()

    # ========== Web API用メソッド ==========

    async def _generate_initial_question(self, phase_num: int) -> str:
        """
        Generate the initial question for a phase.

        Args:
            phase_num: Phase number (1-7)

        Returns:
            Initial question text
        """
        system_prompt = self._get_system_prompt_for_phase(phase_num)
        phase_info = self.phase_mgr.get_phase_info(phase_num)

        context = {
            "conversation_history": "",
            "missing_fields": self.phase_mgr.get_required_fields(phase_num),
            "qa_count": 0,
            "previous_phases": self._load_previous_phase_specs(phase_num)
        }

        return await self._request_question(
            system_prompt, context, f"フェーズ{phase_num}「{phase_info.name}」の初回質問"
        )

    async def _request_question(
        self,
        system_prompt: str,
        context: Dict[str, Any],
        label: str
    ) -> str:
        """
        Ask the LLM for a question, raising instead of substituting a canned one.

        A canned question would look like a real one in the UI, so the user
        could not tell that the LLM call failed (Issue #97).

        Args:
            system_prompt: System prompt for the phase
            context: Context for question generation
            label: What is being generated, used in log and error messages

        Returns:
            Question text (never empty)

        Raises:
            LLMAuthenticationError: If the API key is invalid
            LLMConnectionError: If the LLM service is unreachable
            LLMResponseError: If the call failed otherwise or the response was empty
        """
        try:
            question = await self.llm.generate_question(system_prompt, context)
        except Exception as e:
            logger.error(f"{label}の生成に失敗: {e}")
            raise

        question = (question or "").strip()
        if not question:
            logger.error(f"{label}の生成に失敗: LLM の応答が空でした")
            raise LLMResponseError("LLM の応答が空でした")
        return question

    async def _generate_follow_up_question(
        self,
        phase_num: int,
        context_manager: ContextManager
    ) -> str:
        """
        Generate a follow-up question based on conversation context.

        Args:
            phase_num: Current phase number
            context_manager: Context manager with conversation history

        Returns:
            Follow-up question text
        """
        system_prompt = self._get_system_prompt_for_phase(phase_num)
        context = self._build_context_for_question(phase_num)

        return await self._request_question(
            system_prompt, context, f"フェーズ{phase_num}の次の質問"
        )

    async def _is_phase_complete(
        self,
        phase_num: int,
        context_manager: ContextManager
    ) -> bool:
        """
        Check if a phase has enough information to be completed.

        Args:
            phase_num: Phase number
            context_manager: Context manager with conversation data

        Returns:
            True if phase can be completed
        """
        phase_context = context_manager.get_phase_context(phase_num)
        qa_pairs = phase_context.get("qa_pairs", [])

        # Require at least 3 Q&A pairs
        if len(qa_pairs) < 3:
            return False

        # Use the existing completion check logic
        return await self._check_phase_completion(phase_num)

    async def _generate_and_save_spec(
        self,
        phase_num: int
    ) -> bool:
        """
        Generate and save the specification document for a phase.

        Args:
            phase_num: Phase number

        Returns:
            True when finished. The web router treats None as a client
            disconnect, so this method must not return None.
        """
        # Extract structured data first
        await self._extract_and_save_structured_data(phase_num)

        # Mark phase as complete
        self.context_mgr.mark_phase_complete(phase_num)

        # Generate Markdown spec file using templates
        from spec_ai_writer.generators.markdown_generator import MarkdownGenerator
        from spec_ai_writer.git.git_manager import GitManager

        specs_dir = self.context_mgr.get_specs_dir()
        generator = MarkdownGenerator(specs_dir)
        phase_info = self.phase_mgr.get_phase_info(phase_num)
        structured_data = self.context_mgr.get_structured_data(phase_num)

        if structured_data:
            file_path = generator.generate_spec(
                phase_num,
                phase_info.name,
                phase_info.filename,
                structured_data,
                self.context_mgr.display_name
            )
            print(f"仕様書 {phase_info.filename} を生成しました。")

            # Handle git init on first spec generation and auto-commit
            from spec_ai_writer.config.settings import get_settings
            settings = get_settings()
            if settings.auto_git_commit:
                git_mgr = GitManager(str(specs_dir))
                git_mgr.commit_spec(
                    phase_info.filename,
                    phase_num,
                    phase_info.name
                )

        return True

    def _get_phase_dependencies(self, phase_num: int) -> List[int]:
        """
        Get the list of phases that the current phase depends on.

        Based on SPEC.md section 3.2:
        - Phase 2: depends on Phase 1
        - Phase 3: depends on Phases 1, 2
        - Phase 4: depends on Phases 2, 3
        - Phase 5: depends on Phases 2, 3, 4
        - Phase 6: depends on Phases 2, 5
        - Phase 7: depends on Phase 6

        Args:
            phase_num: Current phase number

        Returns:
            List of phase numbers this phase depends on
        """
        dependencies = {
            1: [],
            2: [1],
            3: [1, 2],
            4: [2, 3],
            5: [2, 3, 4],
            6: [2, 5],
            7: [6],
        }
        return dependencies.get(phase_num, [])

    def _load_previous_phase_specs(self, phase_num: int, max_phases: int = 2) -> str:
        """
        Load specification documents from previous phases that this phase depends on.

        Limits to the most recent `max_phases` dependencies to avoid excessive context size.

        Args:
            phase_num: Current phase number
            max_phases: Maximum number of previous phase specs to include

        Returns:
            Combined content of previous phase specifications
        """
        dependencies = self._get_phase_dependencies(phase_num)
        if not dependencies:
            return ""

        # Limit to most recent dependencies to control context size
        recent_deps = dependencies[-max_phases:]

        specs_dir = self.context_mgr.get_specs_dir()

        specs_content = []
        for dep_phase in recent_deps:
            phase_info = self.phase_mgr.get_phase_info(dep_phase)
            spec_path = specs_dir / phase_info.filename

            if spec_path.exists():
                try:
                    content = spec_path.read_text(encoding="utf-8")
                    specs_content.append(
                        f"### フェーズ{dep_phase}: {phase_info.name}\n\n{content}"
                    )
                except OSError as e:
                    logger.warning(f"仕様書ファイルの読み込みに失敗: {spec_path}: {e}")

        return "\n\n---\n\n".join(specs_content)
