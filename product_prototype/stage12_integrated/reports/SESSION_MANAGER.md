# Optional external manager — PREPARED, NOT ACTIVATED

Installed CLI read-only check: codex-cli0.160.1, `codex exec --help` supports
workspace-write and JSONL. Official [non-interactive documentation](https://learn.chatgpt.com/docs/non-interactive-mode)
confirms that interface. No account credential was read, no API invocation was
made, and no recurring service, cron or detached process was installed.

`scripts/session_manager.py --tag UNIQUE` is dry-run only. Explicit `--execute`
opts into bounded launches; defaults1run/1800seconds, maximum10runs/7200seconds
per run. This is a launch/time budget, NOT a guaranteed token/cost ceiling.
Review project MCP/hooks/config trust before activation; workspace sandbox is
not a replacement for auditing externally configured tools. Permissions are
never bypassed and required approvals may block an unattended child.

Uses flock, rejects dirty tracked files, never resets/stashes work; stops after
two failures/no-progress, timeout, SIGINT/SIGTERM or runtime/STOP. User stop file
persists. Runtime logs are local ignored files, not source/evidence releases.
Progress fingerprint is only a guard, not scientific success. Real release gate
is invoked after a completed cycle. Existing untracked research is preserved.
Actual use requires an authenticated CLI and permission to write its own state;
the read-only PATH alias warning in this environment has not been repaired.
