# Spec AIライター - 仕様駆動開発 インタビュー & 生成システム

[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)

LLM APIを使用してユーザーにインタビューを行い、仕様駆動開発（Specification Driven Development）の7つの仕様書を自動生成するAI支援Pythonプログラムです。

## 特徴

- 🤖 **LLMによる対話形式のインタビュー**: Claude、OpenAI、OpenRouter、Moonshot Kimi、ローカル LLM（Ollama / LM Studio）、AWS Bedrock の 7 プロバイダに対応
- ⚙️ **Web UI からの LLM 設定**: プロバイダ・Base URL・モデル名・API キーをダッシュボードから編集し、サーバー再起動なしで即時反映
- 📝 **「7 つの工程」を段階的に実施**: 原則決定工程から移行・運用工程まで
- 📄 **Markdown仕様書を自動生成**: 各工程終了時に生成
- 🔄 **Git自動コミット**: 生成された仕様書を自動的にコミット
- 💾 **中断・再開機能**: インタビューを途中で保存して後で再開可能
- 🌐 **モダンWeb UI**: React + TypeScriptによるチャットUI
- 🚀 **CLI & Web両対応**: コマンドラインとブラウザから利用可能

### 「7 つの工程」

1. **原則決定工程** (`01-principle-definition.md`) - プロジェクト憲章
2. **企画・要件定義工程** (`02-planning-requirement.md`) - 要件仕様書
3. **設計計画工程** (`03-design-planning.md`) - 設計計画書
4. **タスク分割工程** (`04-task-breakdown.md`) - タスク分割書
5. **実装工程** (`05-implementation.md`) - 実装記録
6. **検証・受入工程** (`06-verification-acceptance.md`) - 検証記録
7. **移行・運用工程** (`07-migration-operation.md`) - 運用記録

### インタビューの流れ

各工程でLLMがインタビューを行い、仕様書を段階的に生成します。

1. 各工程の開始時にLLMが質問を生成
2. あなたが回答を入力（1工程あたり5〜10問）
3. システムが情報を整理し、その工程の仕様書を生成
4. 自動的にGitコミット（設定している場合）
5. 次の工程へ進む

## インストール

### 前提条件

- Python 3.10以上
- [uv](https://docs.astral.sh/uv/) （Pythonパッケージマネージャー）
- LLM API キー、または OpenAI 互換エンドポイント（Claude / OpenAI 公式 / OpenRouter / AWS Bedrock のいずれか）。ローカル LLM（Ollama / LM Studio / llama.cpp）を使う場合は API キー不要

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

`.env`ファイルで以下を設定してください（`.env.example` をコピーして編集）。使用するプロバイダの項目だけ設定すれば OK です:

```env
# アクティブプロバイダ（claude / openai / openrouter / ollama / lmstudio / kimi / bedrock）
DEFAULT_LLM_PROVIDER=claude

# Claude (Anthropic)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
CLAUDE_MODEL=claude-haiku-4-5-20251001

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-5-mini

# OpenRouter
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# Ollama（ローカル LLM）
OLLAMA_MODEL=gemma3:4b
# OLLAMA_BASE_URL=   # 空欄 = http://localhost:11434/v1

# LM Studio（ローカル LLM）
LMSTUDIO_MODEL=local-model
# LMSTUDIO_BASE_URL= # 空欄 = http://localhost:1234/v1

# Moonshot Kimi
KIMI_API_KEY=your_kimi_api_key_here
KIMI_MODEL=kimi-k2.6

# AWS Bedrock
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_REGION=ap-northeast-1

# 共通設定
TEMPERATURE=0.7
DATA_DIR=./data
AUTO_GIT_COMMIT=true
APP_ENV=development
```

> **💡 Web UI からの編集も可能**: 上記の設定はダッシュボードの **「設定」** ページからも編集できます。保存した値は `data/settings.json` にパーミッション `0600` で書き込まれ、環境変数より優先して適用されます。サーバー再起動は不要です（API キーは平文で保存されるため、共有マシンでの使用は避けてください）。

## セキュリティ

**本ツールはローカルホスト（同一マシン）での実行を前提とした開発支援ツールです。ネットワークに公開しないでください。**

- **API に認証・認可はありません**。到達できる者は誰でも、全プロジェクトの閲覧・削除、インタビュー内容の改ざん、LLM プロバイダ設定（API キー・AWS 認証情報を含む）の変更が可能です
- Web サーバーは `127.0.0.1`（ループバック）のみにバインドされ、他のマシンからは到達できません
- API キーは `.env` および `data/settings.json`（パーミッション `0600`）に平文で保存されます。共有マシンでの使用は避けてください

## 使用方法

### Web UI (推奨)

モダンなブラウザUIでインタビューを実施できます。

1. フロントエンドをビルド（初回またはソース変更後のみ）:

```bash
cd frontend
npm install  # 初回のみ
npm run build
cd ..
```

2. spec-ai-writer/ ディレクトリの `.env` に `APP_ENV=production` を設定:

```env
APP_ENV=production
```

3. **バックエンドサーバー起動**:

```bash
uv run python -m spec_ai_writer.web.app
```

ブラウザで http://localhost:8000 を開きます。

#### 開発モード

フロントエンドのソースコードを変更しながらWeb UIを表示する場合、開発モードで起動します。

1. `.env` の `APP_ENV=development` のまま（デフォルト）

2. **バックエンドサーバー起動**:

```bash
# spec-ai-writer/ ディレクトリで
uv run python -m spec_ai_writer.web.app
```

3. **フロントエンド開発サーバー起動** (別ターミナル):

```bash
cd frontend
npm install  # 初回のみ
npm run dev
```

ブラウザで http://localhost:3000 を開きます（Vite が `/api` を localhost:8000 にプロキシ）。

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

#### 起動後の使い方

- ダッシュボードで新規プロジェクト作成（表示名を入力するとプロジェクトIDが自動採番される）
- 「インタビュー開始」ボタンをクリック
- チャット形式でLLMと対話
- 各フェーズ完了時に仕様書が自動生成
- 生成された仕様書をプレビュー・ダウンロード

### CLI (コマンドライン)

ターミナルから直接インタビューを実施できます。

> **初回設定**: `.env` ファイルを編集して API キーと `DEFAULT_LLM_PROVIDER` を設定してください。Web UI を使う場合はダッシュボードの「設定」ページからも設定できます。

1. **インタビュー開始**:

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

以下の 7 プロバイダーに対応しています:

| プロバイダー    | 用途                             |
| --------------- | -------------------------------- |
| **Anthropic**   | クラウド（Claude）               |
| **OpenAI**      | クラウド（ChatGPT）              |
| **OpenRouter**  | クラウド（100 以上のモデル対応） |
| **Moonshot**    | クラウド（Kimi）                 |
| **Ollama**      | ローカル LLM                     |
| **LM Studio**   | ローカル LLM                     |
| **AWS Bedrock** | クラウド（エンタープライズ）     |

各プロバイダーのセットアップ手順は [LLM_SETUP.md](./docs/LLM_SETUP.md) を参照してください。ダッシュボードの **「設定」** ページからもプロバイダの切替と API キー/モデルの編集が可能です。

### コマンド一覧

| コマンド                   | 説明                                                         |
| -------------------------- | ------------------------------------------------------------ |
| `spec start`               | 新規プロジェクト作成とインタビュー開始（表示名を対話で入力） |
| `spec resume <project_id>` | 中断したインタビューを再開                                   |
| `spec list`                | プロジェクト一覧表示（ID・表示名・進捗）                     |
| `spec status <project_id>` | プロジェクトの進捗状況表示                                   |

### グローバルオプション

すべてのコマンドに共通するオプションです。コマンド名の**前**に指定します。

| オプション    | 選択肢                                 | デフォルト | 説明                                               |
| ------------- | -------------------------------------- | ---------- | -------------------------------------------------- |
| `--log-level` | `debug` / `info` / `warning` / `error` | `warning`  | ログ出力レベル。`debug` 時はスタックトレースも表示 |

```bash
spec --log-level=debug start
```

## プロジェクト構造

```
spec-ai-writer/
├── spec_ai_writer/
│   ├── config/
│   │   ├── settings.py              # 設定管理
│   │   └── prompts/                 # 各フェーズのシステムプロンプト
│   ├── templates/                   # Jinja2テンプレート
│   │   ├── 01-principle-definition.md.jinja2
│   │   ├── 02-planning-requirement.md.jinja2
│   │   └── ...
│   ├── core/
│   │   ├── interview_engine.py  # インタビュー制御の中核
│   │   ├── phase_manager.py     # 「7 つの工程」の進行管理
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
black spec_ai_writer/
flake8 spec_ai_writer/
```

### 型チェック

```bash
mypy spec_ai_writer/
```

## アーキテクチャ

### コアコンポーネント

1. **InterviewEngine**: インタビュー全体のオーケストレーション
2. **PhaseManager**: 「7 つの工程」のワークフロー管理
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
