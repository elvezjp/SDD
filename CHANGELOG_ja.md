[English](./CHANGELOG.md) | [日本語](./CHANGELOG_ja.md)

# 変更履歴

このプロジェクトのすべての重要な変更を記録します。

フォーマットは [Keep a Changelog](https://keepachangelog.com/ja/1.0.0/) に基づき、
バージョン管理は [セマンティックバージョニング](https://semver.org/lang/ja/) に準拠しています。

---

## [Unreleased]

### 追加

- **spec-ai-writer / インタビュー入力フォームの改善**: テキストエリアを複数行対応にし、`Shift+Enter` で改行・`Enter` で送信できるようにしました。長い回答を入力しやすくなります（Issue #84 T1–T3）。
- **spec-ai-writer / インタビュー中断ボタン**: 回答中に「中断」ボタンを押すと現在のフェーズを途中で切り上げてトップへ戻れるようになりました（Issue #84 T1–T3）。

### 変更

- **spec-ai-writer / ブランドカラー統一**: UI 全体のカラーテーマをエルブズのブランドカラー（`#3A5CA8`）に統一しました（Issue #84 T7）。
- **spec-ai-writer / プロジェクト説明フィールドを削除**: プロジェクト作成フォームから「説明」フィールドを削除し、入力項目をプロジェクト名のみに絞りました（Issue #84 T6）。

### セキュリティ

- **spec-ai-writer / CSP `connect-src` の厳格化**: `connect-src` を `'self' ws: wss:` から `'self'` に絞りました。本アプリは WebSocket を使用しておらず、任意の `ws:`/`wss:` 接続先を許可する必要がないためです。XSS が成立した場合の情報持ち出し経路を塞ぎます（Issue #91）。
- **spec-ai-writer / 想定利用範囲の明文化**: `README.md` と `SECURITY.md` に、本ツールがローカルホストでの実行を前提としており API に認証機構がないことを明記しました。Web サーバーは `127.0.0.1` のみにバインドされ、他のマシンからは到達できません（Issue #91）。

### 内部変更（ユーザー影響なし）

- **spec-ai-writer / LLM クライアントの非同期化**: `ClaudeClient`・`OpenAIClient`・`BedrockClient` の全クライアントを同期から `async/await` に移行。LLM の応答待ち中も uvicorn のイベントループがブロックされなくなり、プロジェクト一覧の取得など他のリクエストが待たされなくなります。ブラウザが切断した場合（中断ボタン押下など）、処理中の LLM HTTP リクエストをキャンセルし、全プロバイダーでリソースの無駄な消費を停止します。Bedrock は真の非同期キャンセルを実現するため `boto3` から `aiobotocore` に移行しました（Issue #85）。
- **spec-ai-writer / パッケージ構成の整理**: `config/` および `templates/` ディレクトリを `spec_ai_writer/` パッケージ内に移動し、トップレベルの散在を解消しました（Issue #84 T5）。
- **spec-ai-writer / 未使用コードの削除**: 未使用の定数・メソッド・到達不能なコンポーネントを削除しました（Issue #84 T4）。
- **spec-ai-writer / プロンプトファイルの統合**: フェーズごとに分散していた 7 つのプロンプトファイル（`config/prompts/phase_0[1-7]_prompts.py`）を `config/prompts.py` の辞書 1 つに統合しました。
- **spec-ai-writer / `project.json` の廃止**: プロジェクトメタデータを `interview.json` に一元化し、`project.json` を廃止しました。
- **spec-ai-writer / `utils/` ディレクトリの削除**: 中身が空だった `spec_ai_writer/utils/` を削除しました。

---

## [1.0.5] - 2026-06-01

### 変更

- **spec-ai-writer / 依存ライブラリのセキュリティアップデート**: 全 Python およびフロントエンドパッケージを最新化。

---

## [1.0.4] - 2026-04-17

### 追加

- **spec-ai-writer / `--log-level` グローバルオプション**: CLI グループに `--log-level [debug|info|warning|error]`（デフォルト: `warning`）を追加。エラー時のスタックトレースは `--log-level=debug` 指定時のみ表示されるようになり、ファイルパスや API キーの断片が意図せず端末に出力されることを防ぎます。`start`・`resume`・`status`・`_generate_specs` の例外ハンドラをすべて同じパターンに統一しました（Issue #48）。

### 変更

- **spec-ai-writer / 依存ライブラリのセキュリティアップデート**: Dependabotから報告された9件のセキュリティアラート（vite・axios・follow-redirects・black・pytest・Pygments）に対応するため、全PythonおよびフロントエンドパッケージをDependabotアラートの修正バージョンへ更新。未使用パッケージ `python-multipart`（Dependabotアラート #39）と `rich` を `pyproject.toml` から削除（Issue #72）。

### 修正

- **spec-ai-writer / インタビュー途中再開と履歴復元**: インタビュー画面から別画面へ遷移して戻ると、工程の先頭からやり直しになり画面上のチャット履歴がすべて消える不具合を修正。根本原因は、LLM が生成した未回答の質問が `interview.json` に保存されておらず離脱時に失われていたこと。`interview.json` に `pending_question` フィールドを追加し、質問生成直後に保存・回答時に自動クリアする設計に変更。再訪時は保存済みの質問から再開でき、完了済み工程を含むすべての Q&A 履歴が画面に復元されるようになりました (Issue #67)。

---

## [1.0.3] - 2026-04-14

### 追加

- **spec-ai-writer / OpenRouter・ローカル LLM 対応**: 既存の `openai` プロバイダが `OPENAI_BASE_URL` と `OPENAI_MODEL` を受け付けるようになり、OpenAI 公式 API・OpenRouter・OpenAI 互換ローカルサーバー（Ollama, LM Studio, llama.cpp）を単一の経路で扱えるようになりました。`OPENAI_BASE_URL` がローカルエンドポイントを指している場合は `OPENAI_API_KEY` を空欄にできます（Issue #59）。
- **spec-ai-writer / Web UI 設定ページ**: ダッシュボードに新しい `/settings` ページを追加。プロバイダ・Base URL・モデル ID・API キー・Temperature をサーバー再起動なしで編集できます。OpenAI 公式 / OpenRouter / Ollama / LM Studio / カスタムのプリセットを用意（Issue #59）。
- **spec-ai-writer / 設定の永続化レイヤ**: UI から編集した LLM 設定は `data/llm_settings.json` にアトミックに書き込まれ（パーミッション `0600`）、環境変数より優先して適用されます。`GET /api/settings/llm` は API キーをマスクして返し、`PUT /api/settings/llm` は空の API キーを無視するため、マスク表示値を再送信しても保存済みの秘密情報を上書きすることはありません（Issue #59）。

### 変更

- **spec-ai-writer / `reload_settings()`**: グローバル Settings インスタンスを in-place で更新するよう変更。ルーターがモジュールレベルで保持している参照が、プロセス再起動なしで新しい値を観測できるようになりました。
- **spec-ai-writer / `.env.example`**: `OPENAI_BASE_URL` と `OPENAI_MODEL` の項目を追加し、OpenRouter・Ollama・LM Studio 用の使用例を記載。
- **spec-ai-writer / `docs/LLM_SETUP.md`**: OpenRouter およびローカル LLM（Ollama / LM Studio / llama.cpp）のセットアップ章を追加し、Web UI 設定ページに関する注記を追記。

### 修正

- **spec-ai-writer / Python パッケージとフロントエンドのバージョン統一**: `pyproject.toml`・`uv.lock`・`frontend/package.json`・`frontend/package-lock.json`・FastAPI アプリのメタデータ・Click CLI バナー・ダッシュボードフッターのバージョン表記を統一し、すべて **1.0.3** を報告するようになりました（Issue #60）。
- **CONTRIBUTING.md / CONTRIBUTING_ja.md**: 同じ不整合が再発しないよう、一緒にバージョンを上げるべきファイル一覧を含む「spec-ai-writer のリリース手順」セクションを追加しました（Issue #60）。

---

## [1.0.2] - 2026-04-07

### 修正

- **spec-ai-writer / CSP（Content Security Policy）**: 本番モードで127.0.0.1経由アクセス時のCSPエラーを修正（Issue #56）
- **spec-ai-writer / `.env.example`**: APIベースURLの説明を修正（Issue #56）

---

## [1.0.1] - 2026-03-24

### 変更

- **README.md / README_ja.md**: spec-ai-writer セクションを追加し `spec-ai-writer/README.md` へのリンクを記載、日英間でセクション順序を統一
- **spec-ai-writer/README.md**: Python・TypeScript の言語/フレームワークバッジを追加
- **CHANGELOG.md / CONTRIBUTING.md / SECURITY.md**: 英語版デフォルト + `_ja.md` 日本語版に分離し、言語切り替えリンクを追加

---

## [1.0.0] - 2026-02-26

初回リリース。『仕様駆動開発 実践入門』の練習用リポジトリとして公開。

### 追加

- **サンプルファイル（「7 つの工程」）**: 仕様駆動開発の「7 つの工程」に対応したサンプルファイル群（顧客管理システムを題材として）
- **実践ガイド群**: 規模別実践ガイド、90日間導入プラン、セキュリティとプライバシーガイド、トラブルシューティングなど
- **ツール関連ドキュメント**: Cursor関連動画一覧、Gitコマンド一覧、プロンプト集、スクリプト集
- **変換ガイド**: Word/Excel・OASYS/一太郎からMarkdownへの変換ガイド
- **spec-ai-writer**: 仕様駆動開発支援AIツール
- **公開用ドキュメント**: README.md（英語）、README_ja.md（日本語）、CONTRIBUTING.md、SECURITY.md、CHANGELOG.md、LICENSE

### 技術詳細

- 本リポジトリは Markdown ファイルのみで構成（実行可能なコードなし）
- ライセンス: MIT（Copyright (c) 2025 Hideki Tanaka）

---

## リンク

- [リポジトリ](https://github.com/elvezjp/SDD)
- [Issueトラッカー](https://github.com/elvezjp/SDD/issues)

---

## バージョン比較

| バージョン | 主な機能 |
|------------|----------|
| 1.0.5      | 依存ライブラリのセキュリティアップデート（idna 3.15）、CONTRIBUTINGにタグ運用ルールを追記 |
| 1.0.4      | `--log-level` CLIオプション、インタビュー途中再開修正（Issue #48, #67） |
| 1.0.3      | OpenRouter・ローカルLLM対応、Web UI設定ページ、バージョン統一（Issue #59, #60） |
| 1.0.2      | CSP修正、.env.example修正（Issue #56） |
| 1.0.1      | GitHub公開ルール対応：README改善、ドキュメントの日英2ファイル化 |
| 1.0.0      | 初回リリース。「7 つの工程」サンプル、ガイド群、spec-ai-writer、公開用ドキュメント |
