[English](./CHANGELOG.md) | [日本語](./CHANGELOG_ja.md)

# 変更履歴

このプロジェクトのすべての重要な変更を記録します。

フォーマットは [Keep a Changelog](https://keepachangelog.com/ja/1.0.0/) に基づき、
バージョン管理は [セマンティックバージョニング](https://semver.org/lang/ja/) に準拠しています。

---

## [Unreleased]

### 追加

- **spec-ai-writer / Bedrock API キーに対応**: AWS Bedrock を Bedrock API キーで認証できるようにしました。アクセスキーと両方あるときは API キーを使います（Issue #115）。
- **spec-ai-writer / Effort の設定**: 設定画面の「生成パラメータ」で Effort を選べるようにしました。初期値は「自動（モデルの既定）」です。Temperature と Effort は、選んでいるプロバイダとモデルが対応している場合にだけ設定でき、対応していないモデルには送信しません（Issue #113）。

### 変更

- **spec-ai-writer / デフォルトモデルの更新**: 各プロバイダのデフォルトモデルを最新化しました（Claude は Haiku 5.5）。保存済みの設定には影響しません。Temperature は、対応しているモデルにだけ送ります（Issue #101）。
- **spec-ai-writer / LLM クライアントの SDK を更新**: `anthropic` を 2.x、`openai` を 3.x に更新しました。Claude には API バージョン `2026-10-21` で接続し、API キーは `Authorization` ヘッダーで送ります（Issue #112）。

### 修正

- **spec-ai-writer / 拒否・打ち切り・空の応答をエラーにする**: Claude と AWS Bedrock で、モデルが応答を拒否したとき、出力の上限で打ち切られたとき、応答が空のときに、それぞれ原因の分かるエラーにしました（Issue #100）。

---

## [1.0.6] - 2026-11-09

### 追加

- **spec-ai-writer / インタビュー入力の改善**: 複数行の入力（`Shift+Enter` で改行、`Enter` で送信）と、途中で切り上げられる「中断」ボタンを追加しました（Issue #84）。
- **spec-ai-writer / LLM 設定の拡張**: 設定画面で 7 種類のプロバイダを選び、それぞれのモデルや接続情報を設定できるようにしました（Issue #88）。

### 変更

- **spec-ai-writer / 画面の調整**: カラーテーマをブランドカラーに統一し、プロジェクト作成の入力項目をプロジェクト名のみにしました（Issue #84）。
- **spec-ai-writer / 依存ライブラリの更新**: Python とフロントエンドの依存ライブラリを最新化しました。

### 修正

- **spec-ai-writer / Claude 4.7 以降への対応**: Claude 4.7 以降のモデルで AI の呼び出しが失敗する問題を修正しました。Claude と AWS Bedrock には Temperature を送らなくなります（Issue #96）。
- **spec-ai-writer / AI の呼び出しの失敗を画面に表示**: 失敗時に定型文を質問として表示せず、原因を含むエラーを表示するようにしました。失敗した回答は保存しません（Issue #97）。

### セキュリティ

- **spec-ai-writer / CSP の厳格化**: `connect-src` を `'self'` に絞りました（Issue #91）。
- **spec-ai-writer / 想定利用範囲の明文化**: ローカルホストでの実行を前提とし、API に認証がないことを `README.md` と `SECURITY.md` に明記しました（Issue #91）。
- **spec-ai-writer / react-router を v8 に移行**: CSRF バイパスの脆弱性（high）への対応です。本アプリは影響を受けませんが、7.x には修正版がありません。CI の Node は 20 から 22 に上げています。
- **spec-ai-writer / 依存ライブラリのセキュリティ更新**: certifi の critical（侵害されたルート CA の同梱）や GitPython の RCE を含む Dependabot アラートに対応しました（#93, #95）。

### 内部変更（ユーザー影響なし）

- **spec-ai-writer / LLM クライアントの非同期化**: 全クライアントを `async/await` に移行し、中断時に処理中の呼び出しをキャンセルできるようにしました（Issue #85）。
- **spec-ai-writer / コードの整理**: パッケージ構成の整理、未使用コードの削除、プロンプトファイルの統合、`project.json` の廃止を行いました（Issue #84）。

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
| 1.0.6      | Claude 4.7以降への対応、AI呼び出しの失敗を画面に表示、インタビュー入力の改善、LLM設定の7プロバイダ対応、依存ライブラリのセキュリティアップデート |
| 1.0.5      | 依存ライブラリのセキュリティアップデート（idna 3.15）、CONTRIBUTINGにタグ運用ルールを追記 |
| 1.0.4      | `--log-level` CLIオプション、インタビュー途中再開修正（Issue #48, #67） |
| 1.0.3      | OpenRouter・ローカルLLM対応、Web UI設定ページ、バージョン統一（Issue #59, #60） |
| 1.0.2      | CSP修正、.env.example修正（Issue #56） |
| 1.0.1      | GitHub公開ルール対応：README改善、ドキュメントの日英2ファイル化 |
| 1.0.0      | 初回リリース。「7 つの工程」サンプル、ガイド群、spec-ai-writer、公開用ドキュメント |
