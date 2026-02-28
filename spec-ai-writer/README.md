# Spec AIライター - 仕様駆動開発 インタビュー & 生成システム

LLM APIを使用してユーザーにインタビューを行い、仕様駆動開発（Specification Driven Development）の7つの仕様書を自動生成するAI支援Pythonプログラムです。

> **⚠️ 注意: 本ツールはローカル環境での利用を強く推奨します。**
>
> 現在のバージョンにはAPIエンドポイントの認証機構が実装されていないため、外部ネットワークに公開した状態での運用は行わないでください。プロジェクトデータの不正アクセスやLLM APIキーの不正利用につながるリスクがあります。

## 特徴

- 🤖 **LLMによる対話形式のインタビュー**: Claude、OpenAI、AWS Bedrockに対応
- 📝 **7つの工程を段階的に実施**: 原則決定工程から移行・運用工程まで
- 📄 **Markdown仕様書を自動生成**: 各工程終了時に生成
- 🔄 **Git自動コミット**: 生成された仕様書を自動的にコミット
- 💾 **中断・再開機能**: インタビューを途中で保存して後で再開可能
- 🌐 **モダンWeb UI**: React + TypeScriptによるチャットUI
- 🚀 **CLI & Web両対応**: コマンドラインとブラウザから利用可能

## 7つの工程

1. **原則決定工程** (`01-principle-definition.md`) - プロジェクト憲章
2. **企画・要件定義工程** (`02-planning-requirement.md`) - 要件仕様書
3. **設計計画工程** (`03-design-planning.md`) - 設計計画書
4. **タスク分割工程** (`04-task-breakdown.md`) - タスク分割書
5. **実装工程** (`05-implementation.md`) - 実装記録
6. **検証・受入工程** (`06-verification-acceptance.md`) - 検証記録
7. **移行・運用工程** (`07-migration-operation.md`) - 運用記録

## インストール

### 前提条件

- Python 3.9以上
- [uv](https://docs.astral.sh/uv/) （Pythonパッケージマネージャー）
- LLM APIキー（Claude、OpenAI、またはAWS Bedrockのいずれか）

uvをインストールするには:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### セットアップ

1. リポジトリをクローン:
```bash
git clone <repository-url>
cd spec-ai-writer
```

2. 依存パッケージをインストール:
```bash
uv sync
```

開発用依存関係も含める場合:
```bash
uv sync --extra dev
```

3. 環境変数を設定:
```bash
cp .env.example .env
# .envファイルを編集してAPIキーを設定
```

### 環境変数の設定

`.env`ファイルで以下を設定してください:

```env
# LLM APIキー（使用するプロバイダーのキーのみ設定すればOK）
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# AWS Bedrock用（Bedrockを使用する場合）
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_REGION=us-west-2

# 設定
DEFAULT_LLM_PROVIDER=claude  # claude, openai, bedrockから選択
DATA_DIR=./data               # プロジェクトデータの保存先（デフォルト: ./data）
AUTO_GIT_COMMIT=true
TEMPERATURE=0.7
```

## 使用方法

### Web UI (推奨)

モダンなブラウザUIでインタビューを実施できます。

#### モックモード（APIキー不要）

APIキーを設定せずにUIを確認したい場合は、モックモードを使用できます。

1. **フロントエンド開発サーバー起動**:
```bash
cd frontend
npm install  # 初回のみ
VITE_USE_MOCK_API=true npm run dev
```

または、`.env`ファイルを作成:
```env
VITE_USE_MOCK_API=true
```

2. ブラウザで http://localhost:3000 を開きます。

モックモードでは、実際のLLM APIを呼び出さずに、サンプルデータでUIを確認できます。ダッシュボードにはモックモードであることが表示されます。

#### 通常モード（LLM API使用）

実際のLLM APIを使用する場合:

1. **バックエンドサーバー起動**:
```bash
# spec-ai-writer/ ディレクトリで
uv run python -m spec_ai_writer.web.app
```

サーバーが http://localhost:8000 で起動します。

2. **フロントエンド開発サーバー起動** (別ターミナル):
```bash
cd frontend
npm install  # 初回のみ
npm run dev
```

ブラウザで http://localhost:3000 を開きます。

3. **使い方**:
   - ダッシュボードで新規プロジェクト作成（表示名を入力するとプロジェクトIDが自動採番される）
   - 「インタビュー開始」ボタンをクリック
   - チャット形式でLLMと対話
   - 各フェーズ完了時に仕様書が自動生成
   - 生成された仕様書をプレビュー・ダウンロード

### CLI (コマンドライン)

ターミナルから直接インタビューを実施できます。

1. **初期設定** (初回のみ):
```bash
spec init
```

対話形式で設定を行います。

2. **インタビュー開始**:
```bash
spec start
```

プロジェクトの表示名を対話形式で入力します。システムがプロジェクトIDを自動採番し、作成後に表示されます。

3. **インタビュー再開**:
```bash
spec resume <project_id>
```

プロジェクトIDを指定して、中断したインタビューを再開できます。プロジェクトIDは `spec list` で確認できます。

### LLMプロバイダーの設定

Claude (Anthropic API)、OpenAI、AWS Bedrockに対応しています。
各プロバイダーのセットアップ手順は [LLM_SETUP.md](./docs/LLM_SETUP.md) を参照してください。

### コマンド一覧

| コマンド | 説明 |
|---------|------|
| `spec init` | 初期設定ウィザード |
| `spec start` | 新規プロジェクト作成とインタビュー開始（表示名を対話で入力） |
| `spec resume <project_id>` | 中断したインタビューを再開 |
| `spec list` | プロジェクト一覧表示（ID・表示名・進捗） |
| `spec status <project_id>` | プロジェクトの進捗状況表示 |

## プロジェクト構造

```
spec-ai-writer/
├── config/
│   ├── settings.py              # 設定管理
│   └── prompts/                 # 各フェーズのシステムプロンプト
├── spec_ai_writer/
│   ├── core/
│   │   ├── interview_engine.py  # インタビュー制御の中核
│   │   ├── phase_manager.py     # 7つの工程の進行管理
│   │   └── context_manager.py   # コンテキスト管理
│   ├── llm/
│   │   ├── base.py              # LLM抽象インターフェース
│   │   ├── claude_client.py     # Claude API実装
│   │   ├── openai_client.py     # OpenAI API実装
│   │   ├── bedrock_client.py    # AWS Bedrock実装
│   │   └── factory.py           # LLMクライアントファクトリ
│   ├── generators/
│   │   └── markdown_generator.py # Markdown生成
│   └── git/
│       └── git_manager.py       # Git操作
├── templates/                   # Jinja2テンプレート
│   ├── 01-principle-definition.md.jinja2
│   ├── 02-planning-requirement.md.jinja2
│   └── ...
└── data/                        # プロジェクトデータ（DATA_DIR）
    └── {project_id}/
        ├── project.json         # メタ情報（ID、表示名、作成日時、更新日時）
        ├── interview.json       # インタビュー状態（Q&A履歴、工程進捗）
        └── specs/               # 生成された仕様書
            ├── 01-principle-definition.md
            └── ...
```

## 開発

### 開発環境のセットアップ

```bash
uv sync --extra dev
```

### テストの実行

```bash
pytest
```

### コードフォーマット

```bash
black spec_ai_writer/ config/
flake8 spec_ai_writer/ config/
```

### 型チェック

```bash
mypy spec_ai_writer/
```

## アーキテクチャ

### コアコンポーネント

1. **InterviewEngine**: インタビュー全体のオーケストレーション
2. **PhaseManager**: 7つの工程のワークフロー管理
3. **ContextManager**: 質問・回答履歴の管理と永続化
4. **LLMClients**: 複数のLLM API統合（30秒タイムアウト、最大4,096トークン）
5. **MarkdownGenerator**: テンプレートからMarkdown生成
6. **GitManager**: Git自動コミット（プロジェクト単位の `specs/` リポジトリ）

### データフロー

```
User Input → Interview Engine → LLM Client → Question
                ↓
User Answer → Context Manager → Save to data/{project_id}/interview.json
                ↓
Phase Complete → Markdown Generator → Generate Spec File
                ↓                    (data/{project_id}/specs/)
            Git Manager → Auto Commit (specs/ リポジトリ)
```

## ドキュメント

詳細な内部仕様については、[docs/SPEC.md](./docs/SPEC.md) を参照してください。

SPEC.mdには以下の内容が記載されています：
- システム構成とアーキテクチャ
- 機能要件の詳細
- 画面仕様とUI設計
- REST API仕様
- データモデルとスキーマ定義
- 処理フローの詳細
- CLI仕様
- 設定仕様と環境変数

## ライセンス

MIT License

## 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずissueで議論してください。

## サポート

問題が発生した場合は、GitHubのIssuesで報告してください。

## 関連プロジェクト

- [SDD](https://github.com/elvezjp/SDD) - 仕様駆動開発のサンプルリポジトリ

## クレジット

このプロジェクトは『仕様駆動開発 実践入門』の内容に基づいて開発されました。
