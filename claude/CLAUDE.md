# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Instructions

1. Always write to MEMORY, tool calls you made.
2. Use `./.claude/` directory here and not anywhere else.

## Commands

This project uses `uv` (see `uv.lock`) with Python 3.13 (`.python-version`).

- Install/sync dependencies: `uv sync`
- Run the agent: `uv run main.py`
- Add a dependency: `uv add <package>`

There is no lint config, test suite, or test runner configured in this repo currently.

## Architecture

This is a small example project that drives the `claude_agent_sdk` (Python) programmatically, rather than being an app built with it.

- `main.py` is the sole entry point. It calls `query()` from `claude_agent_sdk` to run a single agentic turn and streams the result:
  - `ClaudeAgentOptions.allowed_tools` whitelists which tools the agent may auto-use (`Read`, `Edit`, `Glob`).
  - `permission_mode="bypassPermissions"` auto-approves those tool calls with no user confirmation.
  - `setting_sources=["project"]` makes the SDK load settings/config from this repo (this `CLAUDE.md` and `./.claude/`) instead of user/global config — keep project-specific behavior here rather than relying on global settings.
  - The loop distinguishes `AssistantMessage` (reasoning text and tool-use blocks, printed via `rich.Console`) from the terminal `ResultMessage`.
- `docs/` contains reference documentation fetched from the Agent SDK docs (session storage, structured outputs) used to inform how `main.py`/future code should use those SDK features. It is not runtime code.
- `buggy-code/utils.py` is a standalone sample module (`calculate_average`, `get_user_name`) not imported by `main.py` — treat it as an isolated exercise/fixture, not part of the app.
- `.claude/` is the project-scoped Claude Code config directory (per Instructions above, all Claude-managed state — settings, `MEMORY.md` tool-call log — must live here, not in `~/.claude/`).
- `.env` holds `ANTHROPIC_API_KEY` and is git-ignored; never commit it or print its contents into files/commits.
