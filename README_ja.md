> [!NOTE]
> **Issue・Pull Request について**
> 本リポジトリの [Issues](https://github.com/elvezjp/SDD/issues) や [Pull Requests](https://github.com/elvezjp/SDD/pulls) には、セキュリティ評価や改善提案がそのまま公開されています。
> これらは練習用リポジトリの一部として、実際の開発現場での Issue 管理や PR レビューの参考例としてご活用ください。

# SDD（仕様駆動開発） 練習用リポジトリ

[English](./README.md) | [日本語](./README_ja.md)

[![Elvez](https://img.shields.io/badge/Elvez-Product-3F61A7?style=flat-square)](https://elvez.co.jp/)
[![IXV Ecosystem](https://img.shields.io/badge/IXV-Ecosystem-3F61A7?style=flat-square)](https://elvez.co.jp/ixv/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](https://opensource.org/licenses/MIT)
[![Stars](https://img.shields.io/github/stars/elvezjp/SDD?style=social)](https://github.com/elvezjp/SDD/stargazers)


このリポジトリは、『仕様駆動開発 実践入門』で使用する**練習用リポジトリ**です。このリポジトリについては、本書で「練習用リポジトリ」「SDDリポジトリ」などと呼称しますので、注意してください。

リポジトリ名の「SDD」は「Spec-Driven Development（仕様駆動開発）」の略称です。このリモートリポジトリには、書籍で記載されている「仕様駆動開発の4つの原則と7つの工程」に沿ったサンプルファイルが含まれており、**実際のプロジェクトでどのようにリポジトリを構成するかの参考**になります。

> 本書をお読みの方へ：書籍の誤植・修正事項は[正誤表](./docs/guides/errata.md)をご確認ください。


## このリポジトリの目的

このリモートリポジトリを参考にすることで、仕様駆動開発の全体像を理解しやすくなります。本書を読みながら、実際にCursorを使って仕様を書く練習をしていただくためのリポジトリです。以下のことを体験できます：

- Cursorでのリモートリポジトリのクローンまたはフォーク
- フォークしたリモートリポジトリをローカルリポジトリにクローンして、README.mdを編集
- AIとの対話による仕様の改善
- Git操作（コミット、プッシュ）の基本

**重要**: このリモートリポジトリは参考用です。編集したい場合は、必ずフォーク（Fork）してからご自身のリモートリポジトリをローカルリポジトリにクローンして作業してください。

---

## フォークとクローンの違い（重要）

GitHub には「フォーク（Fork）」と「クローン（Clone）」という似ているが役割の異なる操作があります。**目的に応じて使い分けること**が大切です。

### フォーク（Fork）とは
- このリポジトリを **ご自身の GitHub アカウント配下にコピー**する操作です
- 自分のリポジトリになるため以下のことができるようになります。
  - 自由に編集できる
  - コミット・プッシュが可能
  - 失敗しても元のリポジトリに影響しない

### クローン（Clone）とは
- GitHub 上のリポジトリを **ローカル（PC）にコピー**する操作です
- クローンだけでは、GitHub 上に自分のリポジトリは作られません

### フォークとクローンの違い（整理表）

| 項目 | フォーク（GitHub上での操作） | 直接クローン（ローカリリポジトリに保存をする操作） |
|---|---|---|
| GitHub上に自分のリポジトリが作られる | ✅ | ❌ |
| README.mdを自由に編集してpushできる | ✅ | ❌ |
| 失敗しても元のリポジトリに影響しない | ✅ | ✅ |
| Pull Requestが出せる | ✅ | ❌ |
| 参考・閲覧のみ | △ | ✅ |
| 本リポジトリでの推奨用途 | **編集・練習** | **閲覧のみ** |

## 使い方

### 1. このリモートリポジトリをフォークまたはクローンする

**推奨：フォークする方法**

1. GitHubでこのリモートリポジトリ（https://github.com/elvezjp/SDD）を開く
2. 右上の「Fork」ボタンをクリックして、ご自身のアカウントにフォーク
3. Cursorでフォークしたリモートリポジトリをローカルリポジトリにクローン：
   - Cursorのメニューから「File」>「Clone Repository」を選択
   - フォークしたリモートリポジトリのURLを入力（例：`https://github.com/あなたのユーザー名/SDD.git`）
   - 保存先のフォルダを選択して「Clone」をクリック
Cursor の最新版では、**メニューに「File > Clone Repository」が表示されない場合があります**。
そのため、以下では **コマンドパレット（Command Palette）を使う方法**を案内します。

**参考用にクローンする場合**

1. Cursorのメニューから「File」>「Clone Repository」を選択
2. 以下のURLを入力：
   ```
   https://github.com/elvezjp/SDD.git
   ```
3. 保存先のフォルダを選択
4. 「Clone」をクリック

### 2. README.mdを開いて確認・編集する

クローンまたはフォークが完了したら、左側のエクスプローラーパネルで`README.md`を開いてください。

**注意**: このリモートリポジトリ（elvezjp/SDD）を直接編集することは避けてください。編集したい場合は、必ずフォークしたリモートリポジトリをローカルリポジトリにクローンして作業してください。

### 3. AIと対話しながら仕様を書く

右側のAIチャットパネルで、以下のような質問をしてみてください：

- 「このREADME.mdを読んで、どんな情報を追加すべきか教えてください」
- 「この仕様で不明な点はありますか？」
- 「この書き方で分かりやすいですか？」

### 4. 変更を保存して共有する（フォークしたリモートリポジトリをローカルリポジトリにクローンした場合）

ローカルリポジトリで編集が完了したら：

1. `Ctrl+S`（Macでは`Cmd+S`）で保存
2. AIチャットで「コミットしてプッシュして」と指示する
   - または、Source Controlパネルから手動でコミット・プッシュ

**注意**: このリモートリポジトリ（elvezjp/SDD）への直接のプッシュは行わないでください。フォークしたリモートリポジトリにのみプッシュしてください。

## ディレクトリ構成

このリモートリポジトリは、仕様駆動開発の**4つの原則**と**7つの工程**に沿って構成されています。

```
SDD/
├── README.md                    # このファイル（英語版）
├── README_ja.md                 # 日本語版
├── LICENSE                      # MITライセンス
├── CONTRIBUTING.md              # コントリビューションガイド
├── SECURITY.md                  # セキュリティポリシー
├── CHANGELOG.md                 # バージョン履歴
├── docs/                        # 補足資料
│   ├── README.md               # ガイドの索引
│   ├── conversion/             # 変換ガイド
│   │   ├── markdown-basics.md  # Markdown記法の基本
│   │   ├── word-excel-conversion-guide.md # Word/ExcelからMarkdownへの変換ガイド
│   │   └── oasys-ichitaro-conversion-guide.md # OASYS/一太郎からMarkdownへの変換ガイド
│   ├── tools/                  # ツール関連
│   │   ├── cursor-videos.md    # Cursor関連動画一覧
│   │   ├── git-commands.md     # Gitコマンド一覧
│   │   ├── prompts.md          # プロンプト集（Cursor、GitHub Copilot用）
│   │   └── scripts.md          # スクリプト集（CI/CD設定、Git hooksなど）
│   └── guides/                 # 実践ガイド
│       ├── scale-based-practice-guide.md  # 規模別実践ガイド
│       ├── 90-day-introduction-plan.md    # 90日間導入プラン
│       ├── security-privacy-guide.md      # セキュリティとプライバシーガイド（規制産業・公的機関向け）
│       ├── troubleshooting.md  # トラブルシューティング
│       ├── markdown-friendly-document-creation.md # Markdownにしやすい文書の作り方
│       └── errata.md           # 書籍の正誤表
├── examples/                    # サンプルファイル（7つの工程ごとに1ファイル）
│   ├── 01-principle-definition.md      # 原則決定工程
│   ├── 02-planning-requirement.md      # 企画・要件定義工程
│   ├── 03-design-planning.md            # 設計計画工程
│   ├── 04-task-breakdown.md              # タスク分割工程
│   ├── 05-implementation.md             # 実装工程
│   ├── 06-verification-acceptance.md    # 検証・受入工程
│   ├── 07-migration-operation.md        # 移行・運用工程
│   └── README.md                        # サンプルファイルの説明
└── spec-ai-writer/              # 仕様駆動開発支援AIツール（オプション）
    ├── README.md               # ツールの説明
    ├── QUICKSTART.md           # クイックスタートガイド
    └── ...                     # ツールの実装ファイル
```

## 仕様駆動開発の4つの原則と7つの工程

このリモートリポジトリは、以下の原則と工程に基づいて構成されています：

### 4つの原則

1. **仕様は"生きたドキュメント"**：プロジェクトとともに進化する
2. **仕様は"信頼できる唯一の情報源"**：すべてのメンバーが参照する
3. **仕様は"変更と反復が前提"**：変更履歴を記録しながら更新する
4. **AIでコストを抑える**：AIを活用して仕様の詳細化やレビューを行う

### 7つの工程

各工程ごとに1つのMarkdownファイルで管理します：

1. **原則決定工程**：[`examples/01-principle-definition.md`](examples/01-principle-definition.md)（プロジェクト憲章）
2. **企画・要件定義工程**：[`examples/02-planning-requirement.md`](examples/02-planning-requirement.md)（仕様書）
3. **設計計画工程**：[`examples/03-design-planning.md`](examples/03-design-planning.md)（設計計画）
4. **タスク分割工程**：[`examples/04-task-breakdown.md`](examples/04-task-breakdown.md)（タスク分割）
5. **実装工程**：[`examples/05-implementation.md`](examples/05-implementation.md)（実装記録）
6. **検証・受入工程**：[`examples/06-verification-acceptance.md`](examples/06-verification-acceptance.md)（検証記録）
7. **移行・運用工程**：[`examples/07-migration-operation.md`](examples/07-migration-operation.md)（運用記録）

## サンプルプロジェクト：顧客管理システム

このリモートリポジトリの`examples/`ディレクトリには、サンプルプロジェクトとして「顧客管理システム」の仕様が含まれています。7つの工程すべての例を体験できます：

- **原則決定工程**：プロジェクト憲章の書き方
- **企画・要件定義工程**：仕様書の書き方と、4つの原則に基づく運用
- **設計計画工程**：技術スタックの選定とAI活用の例
- **タスク分割工程**：タスク分解の粒度と進捗管理
- **実装工程**：AIを活用した実装とレビューの記録
- **検証・受入工程**：仕様差分レポートと受入テスト
- **移行・運用工程**：運用改善サイクルとフィードバックの反映

各サンプルファイルには、どの工程の成果物かが明記されています。参考にしてください。

## よくある質問（FAQ）

### Q: このリモートリポジトリを編集できますか？

A: **このリモートリポジトリ（elvezjp/SDD）は参考用のため、直接編集する権限はありません。** 編集を試したい場合は、フォーク（Fork）してご自身のリモートリポジトリをローカルリポジトリにクローンして作業してください。

**フォークの手順**：
1. GitHubでこのリモートリポジトリを開く
2. 右上の「Fork」ボタンをクリック
3. フォークしたリモートリポジトリをローカルリポジトリにクローンして作業する

### Q: エラーが発生した場合はどうすればいいですか？

A: `docs/guides/troubleshooting.md`に、よくあるエラーとその対処法をまとめています。まずはそちらを確認してください。それでも解決しない場合は、GitHubのIssuesで質問してください。

### Q: 第1章で作成したリポジトリと、どちらを使えばいいですか？

A: どちらでも構いません。第1章で既にリポジトリを作成した方は、そちらを使い続けても問題ありません。このリモートリポジトリは、第1章をスキップした方や、新しいリポジトリで練習したい方向けです。

## 本書について

このリモートリポジトリは、以下の書籍で使用されています：

**『仕様駆動開発 実践入門』**

このリポジトリは、本書全体を通じて参照される練習用リポジトリです。主な使用箇所は以下の通りです。

- **はじめに**: 実践的なリソース（スクリプト集、プロンプト集など）の提供元として紹介
- **第2章**: 練習用リポジトリとして詳しく紹介（2.5節「練習用リポジトリ（SDDリポジトリ）を活用する」）
- **第3章**: Cursor関連動画一覧（`docs/tools/cursor-videos.md`）への参照
- **第4章**: Gitコマンド一覧（`docs/tools/git-commands.md`）への参照
- **第5章**: プロンプト集（`docs/tools/prompts.md`）への参照、90日間導入プラン（`docs/guides/90-day-introduction-plan.md`）への参照
- **第10章**: 各種ガイド（Markdown記法、Word/Excel変換、OASYS/一太郎変換など）への参照
- **第11章**: 90日間導入プラン（`docs/guides/90-day-introduction-plan.md`）への参照
- **第12章**: スクリプト集（`docs/tools/scripts.md`）への参照、セキュリティとプライバシーガイド（`docs/guides/security-privacy-guide.md`）への参照
- **第13章**: 90日間導入プラン（`docs/guides/90-day-introduction-plan.md`）への参照、プロンプト集（`docs/tools/prompts.md`）への参照

本書を読みながら、このリポジトリのリソースを活用して仕様駆動開発を実践できます。

## YouTubeチャンネル

私たちは、YouTubeチャンネル「**ソフトウェアの作り方チャンネル Tech千一夜**」を運営しています。

このチャンネルでは、Cursorや仕様駆動開発についての情報発信を行っています。実践的な使い方や最新の情報を動画で解説していますので、ぜひご覧ください。

**チャンネルURL**: https://www.youtube.com/@tech1018/

**Cursor関連動画一覧**: [docs/tools/cursor-videos.md](docs/tools/cursor-videos.md) で、Cursor関連の動画を一覧で確認できます。

## 次のステップ

1. このリモートリポジトリをフォークする（または参考用にローカルリポジトリにクローンする）
2. Cursorでフォークしたリモートリポジトリをローカルリポジトリにクローンして開く
3. README.mdを編集して、あなたのプロジェクトの仕様を書いてみる
4. AIと対話しながら、仕様を育てていく
5. 変更をコミット・プッシュして、フォークしたリモートリポジトリに反映する

---

## リポジトリの保護について

このリモートリポジトリは参考用として保護されています。以下の点にご注意ください：

- **このリモートリポジトリ（elvezjp/SDD）は直接編集しないでください**
- 編集したい場合は、必ずフォーク（Fork）してからご自身のリモートリポジトリをローカルリポジトリにクローンして作業してください
- このリモートリポジトリは、すべての読者が参照できる参考資料として維持されます

---

## ドキュメント

- [CHANGELOG.md](CHANGELOG.md) - バージョン履歴
- [CONTRIBUTING.md](CONTRIBUTING.md) - コントリビューション方法
- [SECURITY.md](SECURITY.md) - セキュリティポリシー

## セキュリティ

セキュリティに関する詳細は [SECURITY.md](SECURITY.md) を参照してください。

- 本リポジトリはドキュメントとサンプルファイルのみで構成されており、実行可能なコードは含みません
- 脆弱性を発見した場合は、公開 Issue ではなくメールでご報告ください（info@elvez.co.jp）

## コントリビューション

コントリビューションを歓迎します。詳細は [CONTRIBUTING.md](CONTRIBUTING.md) を参照してください。

- バグ報告・誤字修正: [GitHub Issues](https://github.com/elvezjp/SDD/issues)
- 機能提案（新サンプル/ガイドの追加など）: [GitHub Issues](https://github.com/elvezjp/SDD/issues)
- プルリクエスト: [GitHub Pull Requests](https://github.com/elvezjp/SDD/pulls)

## 変更履歴

詳細は [CHANGELOG.md](CHANGELOG.md) を参照してください。

## 開発の背景

本ツールは、日本語の開発文書・仕様書を対象とした開発支援AI **IXV（イクシブ）** の開発過程で生まれた小さな実用品です。

IXVでは、システム開発における日本語の文書について、理解・構造化・活用という課題に取り組んでおり、本リポジトリでは、その一部を切り出して公開しています。

## ライセンス

MIT License - 詳細は [LICENSE](LICENSE) を参照してください。

## 問い合わせ先

- **メールアドレス**: info@elvez.co.jp
- **宛先**: 株式会社エルブズ

