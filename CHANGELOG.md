[English](./CHANGELOG.md) | [日本語](./CHANGELOG_ja.md)

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

- **spec-ai-writer / Interview input improvements**: The text area now supports multiple lines — `Shift+Enter` inserts a newline and `Enter` submits, making it easier to write longer answers (Issue #84 T1–T3).
- **spec-ai-writer / Interview stop button**: A "Stop" button lets users end the current phase mid-interview and return to the top page (Issue #84 T1–T3).

### Changed

- **spec-ai-writer / Brand color unification**: Unified the UI color theme to the Elvez brand color (`#3A5CA8`) throughout the application (Issue #84 T7).
- **spec-ai-writer / Removed project description field**: Removed the "description" field from the project creation form, leaving only the project name as required input (Issue #84 T6).
- **spec-ai-writer / Dependency updates**: Updated Python (`uv lock --upgrade`) and frontend (`npm update`) dependencies to their latest versions. Notable updates include anthropic 0.109.2 → 0.120.2, openai 2.42.0 → 2.53.0, fastapi 0.137.1 → 0.141.1, starlette 1.3.1 → 1.4.1, and uvicorn 0.49.0 → 0.52.1.

### Security

- **spec-ai-writer / Tightened CSP `connect-src`**: Narrowed the `connect-src` directive from `'self' ws: wss:` to `'self'`. The application does not use WebSocket, so the allowance for arbitrary `ws:`/`wss:` destinations was unnecessary and would have served as an exfiltration path if XSS ever occurred (Issue #91).
- **spec-ai-writer / Documented the intended usage scope**: `README.md` and `SECURITY.md` now state explicitly that the tool is intended to run on localhost only and that its API has no authentication. The web server binds to `127.0.0.1` only, so it is unreachable from other machines (Issue #91).
- **spec-ai-writer / Migrated to react-router v8**: `react-router-dom` 7.18.2 was affected by a CSRF bypass advisory ([GHSA-qwww-vcr4-c8h2](https://github.com/advisories/GHSA-qwww-vcr4-c8h2), high), so we migrated to `react-router` 8.3.0. The vulnerability is specific to RSC mode and does not affect this application (a client-side SPA), but `react-router-dom` ended at 7.18.2 with no patched release, so the only forward path is v8, where the packages were consolidated. CI Node was bumped from 20 to 22 to meet the v8 requirement (Node 22.22.0+), and routing smoke tests were added.
- **spec-ai-writer / Updated GitPython to 3.1.62**: Addressed five advisories affecting GitPython 3.1.58 and earlier ([GHSA-284h-m62q-gf8w](https://github.com/advisories/GHSA-284h-m62q-gf8w) (critical); [GHSA-7833-fr7j-v32q](https://github.com/advisories/GHSA-7833-fr7j-v32q) and [GHSA-8mcc-hrx5-hvxc](https://github.com/advisories/GHSA-8mcc-hrx5-hvxc) (high); [GHSA-5xxx-qhh7-9287](https://github.com/advisories/GHSA-5xxx-qhh7-9287) and [GHSA-3wxw-xv34-2frg](https://github.com/advisories/GHSA-3wxw-xv34-2frg) (medium)), and raised the minimum version in `pyproject.toml` to `>=3.1.59`. All of them concern git-config writes, clone, blame, submodules, or tag creation; this application only initializes repositories and creates commits, so it does not use any of the affected code paths.
- **spec-ai-writer / Updated vitest to 4.1.11**: Updated `vitest`, `@vitest/coverage-v8`, and `@vitest/ui` to 4.1.11 to address a path traversal vulnerability in `@vitest/mocker` ([GHSA-82fw-gwwq-j7x9](https://github.com/advisories/GHSA-82fw-gwwq-j7x9), medium). Also updated `nanoid` (via `postcss`) to 3.3.19 ([GHSA-2v37-7h3g-55p8](https://github.com/advisories/GHSA-2v37-7h3g-55p8), high). These are development/build-time dependencies only and do not affect the distributed application.
- **spec-ai-writer / Python dependency security updates**: Addressed Dependabot alerts by updating certifi 2026.7.22 → 2026.10.23 (removes compromised emSign root CAs, [GHSA-6q48-6c7w-9gw2](https://github.com/advisories/GHSA-6q48-6c7w-9gw2), critical), GitPython 3.1.62 → 3.2.1 (7 advisories including RCE, [GHSA-83vg-56qc-22m7](https://github.com/advisories/GHSA-83vg-56qc-22m7) and others), aiohttp 3.14.3 → 3.14.5, urllib3 2.7.0 → 2.8.0, multidict 6.7.1 → 6.9.1, and black 26.5.1 → 26.10.1. Raised the minimum versions in `pyproject.toml` to `GitPython>=3.2.1` and `black>=26.10.1`.
- **spec-ai-writer / Frontend dependency security updates**: Addressed Dependabot alerts by updating axios 1.19.0 → 1.21.0 (with follow-redirects 1.16.0 → 1.16.2), vite 8.2.1 → 8.3.5, vitest / `@vitest/coverage-v8` / `@vitest/ui` 4.1.11 → 4.1.12, and the transitive dependencies undici 7.29.0 → 7.30.1, source-map-js 1.2.1 → 1.2.2, and brace-expansion 5.0.9 → 5.0.12. Raised the minimum versions in `package.json` accordingly. Because `@tailwindcss/typography` pins `postcss-selector-parser` to exactly 6.0.10, an `overrides` entry forces it to `^6.1.5` ([GHSA-rj75-hqrm-r3gf](https://github.com/advisories/GHSA-rj75-hqrm-r3gf)). Also updated zod (via `eslint-plugin-react-hooks`) 4.4.3 → 4.6.7 ([GHSA-mrhx-c7xc-m3w5](https://github.com/advisories/GHSA-mrhx-c7xc-m3w5), high).
- **spec-ai-writer / Updated minimatch to 11**: eslint and typescript-eslint depend on minimatch `^10` even in their latest releases, so an `overrides` entry raises it from 10.2.6 to 11.0.4 to address a denial-of-service advisory ([GHSA-g3hv-75wg-m249](https://github.com/advisories/GHSA-g3hv-75wg-m249), moderate). minimatch 11 removes `makeRe` and `AST`, but eslint only uses the `Minimatch` class, `match()`, and `minimatch()`, which remain unchanged. Also updated eslint 10.8.0 → 10.14.0 and typescript-eslint 8.66.0 → 8.72.1. `npm audit` now reports 0 vulnerabilities.

### Internal (no user-facing impact)

- **spec-ai-writer / Async LLM clients**: Converted all LLM clients (`ClaudeClient`, `OpenAIClient`, `BedrockClient`) from synchronous to `async/await`. The uvicorn event loop is no longer blocked during LLM calls, so requests such as fetching the project list respond immediately while the AI is generating. When the browser disconnects (e.g. the user presses the stop button), the in-flight LLM HTTP request is cancelled, stopping unnecessary resource consumption on all providers. Replaced `boto3` with `aiobotocore` for Bedrock to enable true async cancellation (Issue #85).
- **spec-ai-writer / Package restructure**: Moved `config/` and `templates/` directories inside the `spec_ai_writer/` package to eliminate top-level clutter (Issue #84 T5).
- **spec-ai-writer / Dead code removal**: Deleted unused constants, methods, and unreachable components (Issue #84 T4).
- **spec-ai-writer / Prompt file consolidation**: Merged seven per-phase prompt files (`config/prompts/phase_0[1-7]_prompts.py`) into a single `config/prompts.py` dictionary.
- **spec-ai-writer / Retired `project.json`**: Consolidated project metadata into `interview.json`, eliminating the separate `project.json` file.
- **spec-ai-writer / Removed empty `utils/` directory**: Deleted the empty `spec_ai_writer/utils/` directory.

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
| 1.0.5   | Security dependency updates (idna 3.15); tag operation rules added to CONTRIBUTING |
| 1.0.4   | `--log-level` CLI option, interview resume fix (Issue #48, #67) |
| 1.0.3   | OpenRouter & Local LLM support, Web UI settings, version alignment (Issue #59, #60) |
| 1.0.2   | CSP fix, .env.example fix (Issue #56) |
| 1.0.1   | GitHub publication rule compliance: README improvements, doc split into English/Japanese |
| 1.0.0   | Initial release: 7-process samples, practical guides, spec-ai-writer, publication documents |
