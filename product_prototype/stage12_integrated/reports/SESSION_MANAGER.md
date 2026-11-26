# External manager — execution authorized2026-11-26

User explicitly authorized actual automatic follow-up execution, dependencies
within permissions, design/analysis and local commits. No push, SDK mutation,
criteria relaxation, old data deletion, purchase or hardware operation.

Activation budget: at most6 Codex sessions,1800seconds per session (3hours
total child time), no automatic budget renewal. This is a wall-time/launch
budget, not a guaranteed account-token or monetary cap; account limits may
stop it earlier. Same workspace-write sandbox, no bypass flags. One manager
and one research session at a time. Analysis children retain4GiB/420seconds.

Planned external supervisor: transient user systemd service
`regrip-stage12-20261126-1.service`, RuntimeMaxSec10980 (3h+3min cleanup),
MemoryMax8GiB total, CPUQuota200%, TasksMax256, KillModecontrol-group.
The user manager was actually reachable after proper permission escalation;
existing Codex reports logged in with ChatGPT, no MCP servers configured.
Credentials were not opened. Runtime logs/status are local ignored files in
`runtime/authorized_20261126_1/`. Actual active state MUST be checked at
runtime, not inferred from this document. No reboot/login persistence promised.

Stop immediately using either:
`systemctl --user stop regrip-stage12-20261126-1.service`
or create the file `product_prototype/stage12_integrated/runtime/STOP`.
STOP is persistent; the manager never removes it. Do not remove it if the
user requested stopping. No restart policy is installed.

Read `status.json` and `summary.json` in that runtime directory and
`systemctl --user status regrip-stage12-20261126-1.service` for actual state.
Per-run JSONL contains real execution events, not proof of scientific success.
Current source hashes are pinned in the runtime status. A changed manager
source, dirty tracked worktree, branch/history changes, leftover RUNNING task,
time limit, user stop or two failed/no-progress cycles stops further launches.
No automatic reset/stash/cleanup occurs. Unexpected service exceptions remain
visible in the systemd journal; systemd stops its process group.

## Prior preparation (historical)

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
