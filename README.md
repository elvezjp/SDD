> [!NOTE]
> **日本語版をお探しの方へ**
> このリポジトリは書籍『仕様駆動開発 実践入門』の練習用リポジトリです。
> 日本語の README は [README_ja.md](./README_ja.md) をご覧ください。
> **書籍の正誤表は[こちら](./docs/guides/errata.md)です。**

> [!NOTE]
> **Issue・Pull Request について**
> 本リポジトリの [Issues](https://github.com/elvezjp/SDD/issues) や [Pull Requests](https://github.com/elvezjp/SDD/pulls) には、セキュリティ評価や改善提案がそのまま公開されています。
> これらは練習用リポジトリの一部として、実際の開発現場での Issue 管理や PR レビューの参考例としてご活用ください。

# SDD (Spec-Driven Development) Practice Repository

[English](./README.md) | [日本語](./README_ja.md)

[![Elvez](https://img.shields.io/badge/Elvez-Product-3F61A7?style=flat-square)](https://elvez.co.jp/)
[![IXV Ecosystem](https://img.shields.io/badge/IXV-Ecosystem-3F61A7?style=flat-square)](https://elvez.co.jp/ixv/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](https://opensource.org/licenses/MIT)
[![Stars](https://img.shields.io/github/stars/elvezjp/SDD?style=social)](https://github.com/elvezjp/SDD/stargazers)

This repository is the **practice repository** used in *Spec-Driven Development: A Practical Introduction*.
In the book, it is referred to as the "practice repository" or "SDD repository."

The name "SDD" stands for **Spec-Driven Development**. This remote repository contains sample files organized around the "4 Principles and 7 Processes of Spec-Driven Development" described in the book, and serves as **a reference for how to structure a repository in real projects**.

> For readers of the book: Please check the [Errata](./docs/guides/errata.md) for any known corrections.

## Use Cases

By referencing this remote repository, you can better understand the overall picture of Spec-Driven Development.
This repository lets you practice writing specifications with Cursor while reading the book:

- Cloning or forking a remote repository with Cursor
- Editing README.md in your local clone of the forked repository
- Improving specifications through dialogue with AI
- Basic Git operations (commit, push)

**Important**: This remote repository is for reference only. If you want to make edits, always fork it first and then clone your own remote repository to work locally.

---

## Fork vs Clone (Important)

GitHub has two similar but distinct operations: **Fork** and **Clone**. It is important to use each one for the right purpose.

### What is a Fork?
- Copies this repository **under your own GitHub account**
- Since it becomes your own repository, you can:
  - Edit it freely
  - Commit and push changes
  - Work without affecting the original repository

### What is a Clone?
- Copies a GitHub repository **to your local machine (PC)**
- Cloning alone does not create your own repository on GitHub

### Fork vs Clone Comparison

| Item | Fork (operation on GitHub) | Direct Clone (saves to local repository) |
|------|---------------------------|------------------------------------------|
| Creates your own repository on GitHub | ✅ | ❌ |
| Allows free editing and pushing of README.md | ✅ | ❌ |
| Failures don't affect the original repository | ✅ | ✅ |
| Can submit Pull Requests | ✅ | ❌ |
| For reference/viewing only | △ | ✅ |
| Recommended use in this repository | **Editing & Practice** | **Viewing Only** |

## Usage

### 1. Fork or Clone This Remote Repository

**Recommended: Fork**

1. Open this remote repository on GitHub (https://github.com/elvezjp/SDD)
2. Click the "Fork" button in the upper right to fork it to your account
3. Clone your forked repository locally with Cursor:
   - From the Cursor menu, select "File" > "Clone Repository"
   - Enter the URL of your forked repository (e.g., `https://github.com/your-username/SDD.git`)
   - Select a destination folder and click "Clone"

In recent versions of Cursor, **"File > Clone Repository" may not appear in the menu**.
In that case, use the **Command Palette** approach.

**For Reference Only (Direct Clone)**

1. From the Cursor menu, select "File" > "Clone Repository"
2. Enter the following URL:
   ```
   https://github.com/elvezjp/SDD.git
   ```
3. Select a destination folder
4. Click "Clone"

### 2. Open and Review README.md

After cloning or forking, open `README.md` in the left Explorer panel.

**Note**: Avoid editing this remote repository (elvezjp/SDD) directly. If you want to make edits, always fork it first and clone your own remote repository to work locally.

### 3. Write Specifications While Dialoguing with AI

In the AI chat panel on the right, try asking questions like:

- "Please read this README.md and tell me what information should be added."
- "Are there any unclear points in this specification?"
- "Is this written clearly?"

### 4. Save and Share Your Changes (if you cloned your forked repository)

Once you have finished editing locally:

1. Save with `Ctrl+S` (or `Cmd+S` on Mac)
2. Tell the AI chat "commit and push"
   - Or manually commit and push from the Source Control panel

**Note**: Do not push directly to this remote repository (elvezjp/SDD). Only push to your forked repository.

## Features

### 4 Principles

1. **Specifications are "living documents"**: They evolve alongside the project
2. **Specifications are the "single source of truth"**: Referenced by all team members
3. **Specifications assume "change and iteration"**: Updated while recording change history
4. **Reduce costs with AI**: Leverage AI for specification refinement and review

### 7 Processes

Each process is managed in a single Markdown file:

1. **Principle Definition**: [`examples/01-principle-definition.md`](examples/01-principle-definition.md) (Project Charter)
2. **Planning & Requirements**: [`examples/02-planning-requirement.md`](examples/02-planning-requirement.md) (Specification)
3. **Design Planning**: [`examples/03-design-planning.md`](examples/03-design-planning.md) (Design Plan)
4. **Task Breakdown**: [`examples/04-task-breakdown.md`](examples/04-task-breakdown.md) (Task Breakdown)
5. **Implementation**: [`examples/05-implementation.md`](examples/05-implementation.md) (Implementation Log)
6. **Verification & Acceptance**: [`examples/06-verification-acceptance.md`](examples/06-verification-acceptance.md) (Verification Log)
7. **Migration & Operations**: [`examples/07-migration-operation.md`](examples/07-migration-operation.md) (Operations Log)

## Sample Project: Customer Management System

The `examples/` directory contains a sample "Customer Management System" specification covering all 7 processes:

- **Principle Definition**: How to write a project charter
- **Planning & Requirements**: How to write a specification and operate by the 4 principles
- **Design Planning**: Technology stack selection and AI utilization examples
- **Task Breakdown**: Task decomposition granularity and progress management
- **Implementation**: AI-assisted implementation and review records
- **Verification & Acceptance**: Specification diff reports and acceptance testing
- **Migration & Operations**: Operations improvement cycles and feedback integration

Each sample file clearly indicates which process it belongs to.

## Directory Structure

```
SDD/
├── README.md                    # This file (English)
├── README_ja.md                 # Japanese version
├── LICENSE                      # MIT License
├── CONTRIBUTING.md              # Contribution guidelines
├── SECURITY.md                  # Security policy
├── CHANGELOG.md                 # Version history
├── docs/                        # Supplementary materials
│   ├── README.md               # Guide index
│   ├── conversion/             # Conversion guides
│   │   ├── markdown-basics.md  # Markdown basics
│   │   ├── word-excel-conversion-guide.md # Word/Excel to Markdown guide
│   │   └── oasys-ichitaro-conversion-guide.md # OASYS/Ichitaro to Markdown guide
│   ├── tools/                  # Tool-related
│   │   ├── cursor-videos.md    # Cursor video list
│   │   ├── git-commands.md     # Git command reference
│   │   ├── prompts.md          # Prompt collection (for Cursor, GitHub Copilot)
│   │   └── scripts.md          # Script collection (CI/CD settings, Git hooks, etc.)
│   └── guides/                 # Practical guides
│       ├── scale-based-practice-guide.md  # Scale-based practice guide
│       ├── 90-day-introduction-plan.md    # 90-day introduction plan
│       ├── security-privacy-guide.md      # Security and privacy guide (regulated industries/public agencies)
│       ├── troubleshooting.md  # Troubleshooting
│       ├── markdown-friendly-document-creation.md # How to create Markdown-friendly documents
│       └── errata.md           # Book errata
├── examples/                    # Sample files (one file per process)
│   ├── 01-principle-definition.md      # Principle definition process
│   ├── 02-planning-requirement.md      # Planning & requirements process
│   ├── 03-design-planning.md            # Design planning process
│   ├── 04-task-breakdown.md              # Task breakdown process
│   ├── 05-implementation.md             # Implementation process
│   ├── 06-verification-acceptance.md    # Verification & acceptance process
│   ├── 07-migration-operation.md        # Migration & operations process
│   └── README.md                        # Sample file descriptions
└── spec-ai-writer/              # Spec-Driven Development support AI tool (optional)
    ├── README.md               # Tool description
    ├── QUICKSTART.md           # Quick start guide
    └── ...                     # Tool implementation files
```

## FAQ

### Q: Can I edit this remote repository?

A: **This remote repository (elvezjp/SDD) is for reference only, and you do not have permission to edit it directly.** If you want to try editing, fork it first and then clone your forked repository to work locally.

**Fork steps**:
1. Open this remote repository on GitHub
2. Click the "Fork" button in the upper right
3. Clone your forked remote repository locally and work from there

### Q: What should I do if I encounter an error?

A: `docs/guides/troubleshooting.md` contains common errors and their solutions. Please check there first. If the issue remains unresolved, ask a question in GitHub Issues.

### Q: Which should I use—the repository I created in Chapter 1, or this one?

A: Either is fine. If you already created a repository in Chapter 1, you can continue using that. This remote repository is for those who skipped Chapter 1 or want to practice with a fresh repository.

## About the Book

This remote repository is used in the following book:

**"Spec-Driven Development: A Practical Introduction"**

This repository is the practice repository referenced throughout the entire book. Main usage locations:

- **Introduction**: Introduced as a source of practical resources (script collection, prompt collection, etc.)
- **Chapter 2**: Introduced in detail as the practice repository (Section 2.5 "Utilizing the Practice Repository (SDD Repository)")
- **Chapter 3**: Reference to Cursor video list (`docs/tools/cursor-videos.md`)
- **Chapter 4**: Reference to Git command reference (`docs/tools/git-commands.md`)
- **Chapter 5**: Reference to prompt collection (`docs/tools/prompts.md`) and 90-day introduction plan (`docs/guides/90-day-introduction-plan.md`)
- **Chapter 10**: References to various guides (Markdown basics, Word/Excel conversion, OASYS/Ichitaro conversion, etc.)
- **Chapter 11**: Reference to 90-day introduction plan (`docs/guides/90-day-introduction-plan.md`)
- **Chapter 12**: Reference to script collection (`docs/tools/scripts.md`) and security & privacy guide (`docs/guides/security-privacy-guide.md`)
- **Chapter 13**: References to 90-day introduction plan and prompt collection

You can use the resources in this repository to practice Spec-Driven Development while reading the book.

## YouTube Channel

We operate the YouTube channel **"ソフトウェアの作り方チャンネル Tech千一夜"**.

This channel shares information about Cursor and Spec-Driven Development. We explain practical usage and the latest information in video format, so please take a look.

**Channel URL**: https://www.youtube.com/@tech1018/

**Cursor Video List**: [docs/tools/cursor-videos.md](docs/tools/cursor-videos.md) provides a list of Cursor-related videos.

## Next Steps

1. Fork this remote repository (or clone it locally for reference)
2. Open the forked remote repository locally with Cursor
3. Edit README.md and write your project's specifications
4. Grow your specifications through dialogue with AI
5. Commit and push changes to reflect them in your forked remote repository

---

## Repository Protection

This remote repository is maintained for reference. Please note the following:

- **Do not edit this remote repository (elvezjp/SDD) directly**
- If you want to make edits, always fork it first and clone your own remote repository to work locally
- This remote repository is maintained as a reference resource for all readers

---

## Documentation

- [CHANGELOG.md](CHANGELOG.md) - Version history
- [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute
- [SECURITY.md](SECURITY.md) - Security policy

## Security

For security details, see [SECURITY.md](SECURITY.md).

- This repository consists solely of documentation and sample files; no executable code is included
- If you discover a vulnerability, please report it by email rather than opening a public Issue (info@elvez.co.jp)

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

- Bug reports / typo fixes: [GitHub Issues](https://github.com/elvezjp/SDD/issues)
- Feature proposals (new samples/guides, etc.): [GitHub Issues](https://github.com/elvezjp/SDD/issues)
- Pull requests: [GitHub Pull Requests](https://github.com/elvezjp/SDD/pulls)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for details.

## Background

This tool was created as a small utility during the development of **IXV (Ixiv)**, a development support AI for Japanese development documents and specifications.

IXV addresses the challenges of understanding, structuring, and utilizing Japanese documents in system development. This repository publishes a portion of that work.

## License

MIT License - See [LICENSE](LICENSE) for details.

## Contact

- **Email**: info@elvez.co.jp
- **Recipient**: Elvez Inc. (株式会社エルブズ)
