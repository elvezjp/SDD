/**
 * Mock API Client for Development/Demo
 *
 * Provides mock data when API keys are not configured
 */

import type {
  Project,
  ProjectCreate,
  ProjectListResponse,
  ProjectStatusResponse,
  PhaseStatus,
  InterviewStartRequest,
  InterviewStartResponse,
  UserAnswerRequest,
  AssistantQuestionResponse,
  SpecificationResponse,
  SpecificationListResponse,
  LLMProvider,
  ProviderSettingsResponse,
  SettingsResponse,
  SettingsUpdateRequest,
  GenerationParamsResponse,
} from "@/types";

// Simulate network delay
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

// Simple ID generator for mock
let nextIdCounter = 100;
function generateMockId(): string {
  nextIdCounter++;
  return `mock_${nextIdCounter}`;
}

class MockAPIClient {
  private mockProjects: Project[] = [
    {
      project_id: "demo_001",
      display_name: "demo-project",
      current_phase: 3,
      phase_status: {
        1: "completed",
        2: "completed",
        3: "in_progress",
        4: "not_started",
        5: "not_started",
        6: "not_started",
        7: "not_started",
      },
      created_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
      updated_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
      total_qa_pairs: 15,
    },
    {
      project_id: "sample_002",
      display_name: "sample-webapp",
      current_phase: 7,
      phase_status: {
        1: "completed",
        2: "completed",
        3: "completed",
        4: "completed",
        5: "completed",
        6: "completed",
        7: "completed",
      },
      created_at: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(),
      updated_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
      total_qa_pairs: 42,
    },
  ];

  private mockAnswerCounts: Record<string, number> = {};

  async healthCheck() {
    await delay(300);
    return {
      status: "healthy",
      llm_provider: "mock",
      mode: "mock",
    };
  }

  async listProjects(): Promise<ProjectListResponse> {
    await delay(500);
    return {
      projects: [...this.mockProjects],
      total: this.mockProjects.length,
    };
  }

  async getProject(projectId: string): Promise<Project> {
    await delay(300);
    const project = this.mockProjects.find((p) => p.project_id === projectId);
    if (!project) {
      throw new Error(`Project not found: ${projectId}`);
    }
    return { ...project };
  }

  async getProjectStatus(projectId: string): Promise<ProjectStatusResponse> {
    await delay(300);
    const project = this.mockProjects.find((p) => p.project_id === projectId);
    if (!project) {
      throw new Error(`Project not found: ${projectId}`);
    }

    const phases = [
      {
        phase_num: 1,
        phase_name: "原則決定工程",
        description: "プロジェクトの基本原則を定義",
        status: project.phase_status[1] as PhaseStatus,
        qa_count: 3,
        required_fields: [],
        filename: "01-principle-definition.md",
      },
      {
        phase_num: 2,
        phase_name: "企画・要件定義",
        description: "要件を明確化",
        status: project.phase_status[2] as PhaseStatus,
        qa_count: 5,
        required_fields: [],
        filename: "02-planning-requirement.md",
      },
      {
        phase_num: 3,
        phase_name: "設計計画",
        description: "設計方針を決定",
        status: project.phase_status[3] as PhaseStatus,
        qa_count: 4,
        required_fields: [],
        filename: "03-design-planning.md",
      },
      {
        phase_num: 4,
        phase_name: "タスク分割",
        description: "作業を細分化",
        status: project.phase_status[4] as PhaseStatus,
        qa_count: 0,
        required_fields: [],
        filename: "04-task-breakdown.md",
      },
      {
        phase_num: 5,
        phase_name: "実装",
        description: "実装を進める",
        status: project.phase_status[5] as PhaseStatus,
        qa_count: 0,
        required_fields: [],
        filename: "05-implementation.md",
      },
      {
        phase_num: 6,
        phase_name: "検証・受入",
        description: "テストと検証",
        status: project.phase_status[6] as PhaseStatus,
        qa_count: 0,
        required_fields: [],
        filename: "06-verification-acceptance.md",
      },
      {
        phase_num: 7,
        phase_name: "移行・運用",
        description: "本番環境への移行",
        status: project.phase_status[7] as PhaseStatus,
        qa_count: 0,
        required_fields: [],
        filename: "07-migration-operation.md",
      },
    ];

    const completedCount = phases.filter(
      (p) => p.status === "completed",
    ).length;
    return {
      project_id: projectId,
      current_phase: project.current_phase,
      phases,
      overall_progress: Math.round((completedCount / 7) * 100),
    };
  }

  async createProject(data: ProjectCreate): Promise<Project> {
    await delay(500);
    const newProject: Project = {
      project_id: generateMockId(),
      display_name: data.display_name,
      current_phase: 1,
      phase_status: {
        1: "not_started",
        2: "not_started",
        3: "not_started",
        4: "not_started",
        5: "not_started",
        6: "not_started",
        7: "not_started",
      },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      total_qa_pairs: 0,
    };
    this.mockProjects.push(newProject);
    return { ...newProject };
  }

  async deleteProject(projectId: string): Promise<void> {
    await delay(300);
    this.mockProjects = this.mockProjects.filter(
      (p) => p.project_id !== projectId,
    );
  }

  async startInterview(
    data: InterviewStartRequest,
  ): Promise<InterviewStartResponse> {
    await delay(800);
    const phaseNum = data.phase_num || 1;
    const phaseNames = [
      "原則決定工程",
      "企画・要件定義",
      "設計計画",
      "タスク分割",
      "実装",
      "検証・受入",
      "移行・運用",
    ];
    // Reset answer count for this project
    this.mockAnswerCounts[data.project_id] = 0;
    return {
      project_id: data.project_id,
      display_name: data.project_id,
      phase_num: phaseNum,
      phase_name: phaseNames[phaseNum - 1],
      initial_message: `こんにちは！フェーズ${phaseNum}「${phaseNames[phaseNum - 1]}」のインタビューを開始します。\n\nまず、プロジェクトの概要について教えてください。`,
    };
  }

  async submitAnswer(
    data: UserAnswerRequest,
  ): Promise<AssistantQuestionResponse> {
    await delay(1000);
    // Track answer count per project for mock progression
    if (!this.mockAnswerCounts[data.project_id]) {
      this.mockAnswerCounts[data.project_id] = 0;
    }
    this.mockAnswerCounts[data.project_id]++;
    const count = this.mockAnswerCounts[data.project_id];

    const mockQuestions = [
      "ありがとうございます。次に、プロジェクトの主要な目的について詳しく教えてください。",
      "理解しました。では、このプロジェクトで最も重要な成功基準は何でしょうか？",
      "素晴らしいですね。最後に、プロジェクトの制約事項があれば教えてください。",
    ];

    const isPhaseComplete = count >= 3;

    return {
      question: isPhaseComplete
        ? "フェーズが完了しました。次のフェーズに進みます。"
        : mockQuestions[Math.min(count - 1, mockQuestions.length - 1)],
      phase_complete: isPhaseComplete,
      phase_num: 1,
      qa_count: count,
    };
  }

  async listSpecifications(
    projectId: string,
  ): Promise<SpecificationListResponse> {
    await delay(400);
    const project = this.mockProjects.find((p) => p.project_id === projectId);
    if (!project) {
      throw new Error(`Project not found: ${projectId}`);
    }

    const phaseNames = [
      "原則決定工程",
      "企画・要件定義",
      "設計計画",
      "タスク分割",
      "実装",
      "検証・受入",
      "移行・運用",
    ];

    const filenames = [
      "01-principle-definition.md",
      "02-planning-requirement.md",
      "03-design-planning.md",
      "04-task-breakdown.md",
      "05-implementation.md",
      "06-verification-acceptance.md",
      "07-migration-operation.md",
    ];

    const specifications = filenames.map((filename, index) => ({
      phase_num: index + 1,
      phase_name: phaseNames[index],
      filename,
      file_size:
        project.phase_status[index + 1] === "completed"
          ? 15000 + Math.random() * 10000
          : undefined,
      generated_at:
        project.phase_status[index + 1] === "completed"
          ? new Date(
              Date.now() - (7 - index) * 24 * 60 * 60 * 1000,
            ).toISOString()
          : undefined,
      exists: project.phase_status[index + 1] === "completed",
    }));

    return {
      project_id: projectId,
      specifications,
    };
  }

  async getSpecification(
    projectId: string,
    phaseNum: number,
  ): Promise<SpecificationResponse> {
    await delay(400);
    const phaseNames = [
      "原則決定工程",
      "企画・要件定義",
      "設計計画",
      "タスク分割",
      "実装",
      "検証・受入",
      "移行・運用",
    ];
    const filenames = [
      "01-principle-definition.md",
      "02-planning-requirement.md",
      "03-design-planning.md",
      "04-task-breakdown.md",
      "05-implementation.md",
      "06-verification-acceptance.md",
      "07-migration-operation.md",
    ];

    return {
      project_id: projectId,
      phase_num: phaseNum,
      phase_name: phaseNames[phaseNum - 1],
      filename: filenames[phaseNum - 1],
      content: `# ${phaseNames[phaseNum - 1]}\n\n## 概要\n\nこれはモックモードで表示されているサンプル仕様書です。\n\n実際の仕様書を生成するには、LLM APIキーを設定してバックエンドサーバーを起動してください。\n\n## プロジェクト情報\n\n- プロジェクトID: ${projectId}\n- フェーズ: ${phaseNum}\n\n## 内容\n\nこの仕様書は、実際のインタビューを通じて生成されます。\n\nモックモードでは、実際のLLM APIを呼び出さないため、このサンプルコンテンツが表示されています。`,
      generated_at: new Date().toISOString(),
    };
  }

  async downloadSpecification(
    projectId: string,
    phaseNum: number,
  ): Promise<Blob> {
    await delay(500);
    const spec = await this.getSpecification(projectId, phaseNum);
    return new Blob([spec.content], { type: "text/markdown" });
  }

  async downloadAllSpecifications(projectId: string): Promise<Blob> {
    await delay(800);
    const list = await this.listSpecifications(projectId);
    const completedSpecs = list.specifications.filter((s) => s.exists);
    const content = completedSpecs
      .map((s) => `# ${s.phase_name}\n\n[仕様書内容]\n\n`)
      .join("\n\n---\n\n");
    return new Blob([content], { type: "text/markdown" });
  }

  async resetPhase(data: {
    project_id: string;
    phase_num: number;
  }): Promise<{ project_id: string; phase_num: number; message: string }> {
    await delay(500);
    return {
      project_id: data.project_id,
      phase_num: data.phase_num,
      message: `フェーズ ${data.phase_num} をリセットしました。再インタビューを開始できます。`,
    };
  }

  // Settings API (mock)
  private mockSettings: SettingsResponse = {
    active_provider: "claude",
    temperature: 0.7,
    effort: "auto",
    providers: {
      claude: {
        model: "claude-haiku-4-5-20251001",
        api_key_masked: "sk-a****mock",
        base_url: "",
        aws_access_key_id_masked: "",
        aws_secret_access_key_masked: "",
        aws_region: "",
      },
      openai: {
        model: "gpt-5-mini",
        api_key_masked: "",
        base_url: "",
        aws_access_key_id_masked: "",
        aws_secret_access_key_masked: "",
        aws_region: "",
      },
      openrouter: {
        model: "",
        api_key_masked: "",
        base_url: "",
        aws_access_key_id_masked: "",
        aws_secret_access_key_masked: "",
        aws_region: "",
      },
      ollama: {
        model: "gemma3:4b",
        api_key_masked: "",
        base_url: "http://localhost:11434/v1",
        aws_access_key_id_masked: "",
        aws_secret_access_key_masked: "",
        aws_region: "",
      },
      lmstudio: {
        model: "",
        api_key_masked: "",
        base_url: "http://localhost:1234/v1",
        aws_access_key_id_masked: "",
        aws_secret_access_key_masked: "",
        aws_region: "",
      },
      kimi: {
        model: "kimi-k2.6",
        api_key_masked: "",
        base_url: "",
        aws_access_key_id_masked: "",
        aws_secret_access_key_masked: "",
        aws_region: "",
      },
      bedrock: {
        model: "jp.anthropic.claude-haiku-4-5",
        api_key_masked: "",
        base_url: "",
        aws_access_key_id_masked: "",
        aws_secret_access_key_masked: "",
        aws_region: "ap-northeast-1",
      },
    } as Record<LLMProvider, ProviderSettingsResponse>,
    sources: {},
  };

  async getSettings(): Promise<SettingsResponse> {
    await delay(200);
    return {
      ...this.mockSettings,
      providers: { ...this.mockSettings.providers } as Record<
        LLMProvider,
        ProviderSettingsResponse
      >,
    };
  }

  async getGenerationParams(
    provider: LLMProvider,
    model: string,
  ): Promise<GenerationParamsResponse> {
    await delay(100);
    const isClaude = provider === "claude" || provider === "bedrock";
    return {
      model,
      temperature_supported: !isClaude,
      effort_levels: isClaude ? ["low", "medium", "high"] : [],
    };
  }

  async updateSettings(data: SettingsUpdateRequest): Promise<SettingsResponse> {
    await delay(300);
    if (data.effort) this.mockSettings.effort = data.effort;
    if (data.active_provider)
      this.mockSettings.active_provider = data.active_provider;
    if (data.temperature !== undefined)
      this.mockSettings.temperature = data.temperature;
    if (data.providers) {
      for (const [key, update] of Object.entries(data.providers)) {
        const p = key as LLMProvider;
        const current = this.mockSettings.providers[p];
        if (!current || !update) continue;
        if (update.model !== undefined) current.model = update.model;
        if (update.base_url !== undefined) current.base_url = update.base_url;
        if (update.aws_region !== undefined)
          current.aws_region = update.aws_region;
        if (update.api_key)
          current.api_key_masked = `${update.api_key.slice(0, 4)}****mock`;
        if (update.aws_access_key_id)
          current.aws_access_key_id_masked = "AKIA****mock";
        if (update.aws_secret_access_key)
          current.aws_secret_access_key_masked = "****mock";
      }
    }
    return {
      ...this.mockSettings,
      providers: { ...this.mockSettings.providers } as Record<
        LLMProvider,
        ProviderSettingsResponse
      >,
    };
  }
}

export const mockApiClient = new MockAPIClient();
export default mockApiClient;
