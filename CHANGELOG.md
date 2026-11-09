[English](./CHANGELOG.md) | [日本語](./CHANGELOG_ja.md)

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [1.0.6] - 2026-11-09

### Added

- **spec-ai-writer / Interview input improvements**: Added multi-line input (`Shift+Enter` for a newline, `Enter` to submit) and a "Stop" button to end a phase midway (Issue #84).
- **spec-ai-writer / Expanded LLM settings**: The Settings screen now supports seven providers, each with its own model and connection settings (Issue #88).

### Changed

- **spec-ai-writer / UI adjustments**: Unified the color theme to the brand color and reduced project creation to the project name only (Issue #84).
- **spec-ai-writer / Dependency updates**: Updated Python and frontend dependencies to their latest versions.

### Fixed

- **spec-ai-writer / Claude 4.7 and later support**: Fixed AI calls failing on Claude 4.7 and later. `temperature` is no longer sent to Claude or AWS Bedrock (Issue #96).
- **spec-ai-writer / Show LLM failures in the UI**: When an LLM call fails, the app shows an error with the cause instead of a canned question, and does not keep the answer (Issue #97).

### Security

- **spec-ai-writer / Tightened CSP**: Narrowed `connect-src` to `'self'` (Issue #91).
- **spec-ai-writer / Documented the intended usage scope**: `README.md` and `SECURITY.md` now state that the tool is intended for localhost and that its API has no authentication (Issue #91).
- **spec-ai-writer / Migrated to react-router v8**: Addresses a CSRF bypass advisory (high). It does not affect this application, but 7.x has no patched release. CI Node was raised from 20 to 22.
- **spec-ai-writer / Dependency security updates**: Addressed Dependabot alerts, including a critical one in certifi (compromised root CAs) and an RCE in GitPython (#93, #95).

### Internal (no user-facing impact)

- **spec-ai-writer / Async LLM clients**: Converted all LLM clients to `async/await`, so in-flight calls can be cancelled when an interview is stopped (Issue #85).
- **spec-ai-writer / Code cleanup**: Restructured packages, removed unused code, consolidated prompt files, and retired `project.json` (Issue #84).

---

## [1.0.5] - 2026-06-01

### Changed

- **spec-ai-writer / Dependency security updates**: Updated all Python and frontend packages to the latest compatible versions.

---

## [1.0.4] - 2026-04-17

### Added

- **spec-ai-writer / `--log-level` global option**: Added `--log-level [debug|info|warning|error]` (default: `warning`) to the CLI group. Stack traces are now shown only when `--log-level=debug` is specified, preventing accidental exposure of file paths or API key fragments on error. Exception handlers across all commands (`start`, `resume`, `status`, `_generate_specs`) have been unified to follow the same pattern (Issue #48).

### Changed

- **spec-ai-writer / Dependency security updates**: Updated all Python and frontend dependencies to the latest compatible versions to address 9 Dependabot security alerts (vite, axios, follow-redirects, black, pytest, Pygments). Removed unused packages `python-multipart` (Dependabot alert #39) and `rich` from `pyproject.toml` (Issue #72).

### Fixed

- **spec-ai-writer / Interview resume from mid-phase**: When a user navigated away from the interview screen mid-phase and returned, the interview restarted from the first question of that phase and all chat history was lost. Root cause: the pending (unanswered) question was never persisted, so only already-answered Q&A pairs were stored. Fixed by adding a `pending_question` field to `interview.json` that is written immediately after each question is generated and cleared when the user answers. On resume, the stored pending question is returned and the full Q&A history (including completed phases) is restored on screen (Issue #67).

---

## [1.0.3] - 2026-04-14

### Added

- **spec-ai-writer / OpenRouter & Local LLM support**: The existing `openai` provider now accepts `OPENAI_BASE_URL` and `OPENAI_MODEL`, making it a unified path for the official OpenAI API, OpenRouter, and OpenAI-compatible local servers (Ollama, LM Studio, llama.cpp). When `OPENAI_BASE_URL` points at a local endpoint, `OPENAI_API_KEY` may be left empty (Issue #59).
- **spec-ai-writer / Web UI settings page**: New `/settings` page in the dashboard lets users edit the active provider, base URL, model ID, API keys and temperature without restarting the server. Presets are provided for OpenAI Official / OpenRouter / Ollama / LM Studio / Custom (Issue #59).
- **spec-ai-writer / Settings persistence layer**: LLM settings edited from the UI are written atomically to `data/llm_settings.json` with `0600` permissions and overlaid on top of environment variables. `GET /api/settings/llm` returns masked API keys; `PUT /api/settings/llm` ignores empty key fields so re-submitting a masked display value never overwrites the stored secret (Issue #59).

### Changed

- **spec-ai-writer / `reload_settings()`**: Now mutates the existing global Settings instance in place so that module-level references captured by routers observe the updated values without a process restart.
- **spec-ai-writer / `.env.example`**: Added `OPENAI_BASE_URL` and `OPENAI_MODEL` entries with usage examples for OpenRouter, Ollama and LM Studio.
- **spec-ai-writer / `docs/LLM_SETUP.md`**: Added OpenRouter and Local LLM (Ollama / LM Studio / llama.cpp) setup sections and a note about the Web UI settings page.

### Fixed

- **spec-ai-writer / Version alignment between Python package and frontend**: Unified the `spec-ai-writer` version across `pyproject.toml`, `uv.lock`, `frontend/package.json`, `frontend/package-lock.json`, the FastAPI app metadata, the Click CLI banner and the dashboard footer. All now report **1.0.3** (Issue #60).
- **CONTRIBUTING.md / CONTRIBUTING_ja.md**: Added a "Releasing spec-ai-writer" section documenting which files must be bumped together so this desynchronization cannot recur (Issue #60).

---

## [1.0.2] - 2026-04-07

### Fixed

- **spec-ai-writer / CSP (Content Security Policy)**: Fixed CSP error when accessing via 127.0.0.1 in production mode (Issue #56)
- **spec-ai-writer / `.env.example`**: Fixed API base URL description (Issue #56)

---

## [1.0.1] - 2026-03-24

### Changed

- **README.md / README_ja.md**: Added spec-ai-writer section with link to `spec-ai-writer/README.md` and unified section order between English and Japanese versions
- **spec-ai-writer/README.md**: Added Python and TypeScript language/framework badges
- **CHANGELOG.md / CONTRIBUTING.md / SECURITY.md**: Split into English default + `_ja.md` Japanese versions with language switch links

---

## [1.0.0] - 2026-02-26

Initial release. Published as the practice repository for *Spec-Driven Development: A Practical Introduction*.

### Added

- **Sample files (7 processes)**: Sample files for all 7 processes of Spec-Driven Development (using a Customer Management System as the subject)
- **Practical guides**: Scale-based practice guide, 90-day introduction plan, security and privacy guide, troubleshooting guide, and more
- **Tool documentation**: Cursor video list, Git command reference, prompt collection, script collection
- **Conversion guides**: Word/Excel and OASYS/Ichitaro to Markdown conversion guides
- **spec-ai-writer**: AI tool for Spec-Driven Development support
- **Publication documents**: README.md (English), README_ja.md (Japanese), CONTRIBUTING.md, SECURITY.md, CHANGELOG.md, LICENSE

### Technical Details

- This repository consists solely of Markdown files (no executable code)
- License: MIT (Copyright (c) 2025 Hideki Tanaka)

---

## Links

- [Repository](https://github.com/elvezjp/SDD)
- [Issue Tracker](https://github.com/elvezjp/SDD/issues)

---

## Version Comparison

| Version | Key Features |
|---------|-------------|
| 1.0.6   | Claude 4.7+ support, LLM failures shown in the interview UI, interview input improvements, seven-provider LLM settings, security dependency updates |
| 1.0.5   | Security dependency updates (idna 3.15); tag operation rules added to CONTRIBUTING |
| 1.0.4   | `--log-level` CLI option, interview resume fix (Issue #48, #67) |
| 1.0.3   | OpenRouter & Local LLM support, Web UI settings, version alignment (Issue #59, #60) |
| 1.0.2   | CSP fix, .env.example fix (Issue #56) |
| 1.0.1   | GitHub publication rule compliance: README improvements, doc split into English/Japanese |
| 1.0.0   | Initial release: 7-process samples, practical guides, spec-ai-writer, publication documents |
