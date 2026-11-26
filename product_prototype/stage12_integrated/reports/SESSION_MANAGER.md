# External manager — execution authorized2026-11-26

## NEW allocation4 — user-approved10 x3600seconds

The latest explicit user instruction authorizes a **separate** allocation:
`authorized_20261126_4`, service `regrip-stage12-20261126-4.service`.
Maximum10 launches,3600seconds per worker,36000 total research-child seconds.
RuntimeMaxSec36900 includes up to900seconds supervisor/audit/cleanup overhead;
it does not authorize more research. Restart=no, no automatic budget renewal.
Old six-session allocation and all prior runtime logs remain preserved.
See AUTOMATION_AUTHORIZATION_20261126_4.json for source pins and policy.

Primary candidate RevAK235; Collet capacity, protected peak, actual whole Palm,
Idler and Finger load response, same-revision Stage1/2 revalidation. Maintain
track balance rather than generic rod refinement. No security/source changes
to manager or supervisor are needed. Worker still submits complete exact
SHA256 save manifest; supervisor performs the guarded local commit.

Actual activity must be read from new runtime status.json and systemd, not
from this authorization. Stop via shared runtime/STOP or:
`systemctl --user stop regrip-stage12-20261126-4.service`.
Do not delete STOP or clear it automatically. Check no existing manager,
available flock, clean tracked state and no RUNNING tasks before first launch.
Official [non-interactive documentation](https://learn.chatgpt.com/docs/non-interactive-mode)
was rechecked; installed codex-cli0.160.1 still supports workspace-write exec.

## Recovery / remaining budget

LATEST: service2 completed actual distributed-contact research, then rejected
its save because the two AGENTS-referenced root handoff reports were missing
from the exact allowlist. No permission or physics check was weakened. Only
reports/INTEGRATED_CURRENT_STATUS.md and reports/INTEGRATED_NEXT_TASKS.md were
added. Result paths may be strings only if they uniquely resolve to an already
SHA256-verified file record. manager_flow2 executes TWO actual isolated loops
with precisely these common-report edits and string result paths; both commit
and continue. Research outputs, including coarse mesh FAIL, saved in1afffcb.

Current relaunch: service regrip-stage12-20261126-3.service, runtime
authorized_20261126_3. Remaining ORIGINAL allocation4x1800s (2hours total child
time), RuntimeMaxSec7380. The two earlier actual cycles count against the
original6; software-only isolated tests do not consume Codex launches.
Stop: `systemctl --user stop regrip-stage12-20261126-3.service` or persistent
runtime/STOP. Check actual status, not the historical service names below.

First actual service stopped after1cycle, not because research was complete:
child .git is protected read-only. Its9case elastic terminal reference and
failures were inspected and saved in f5225df. The empty staging guard was
never represented as guarding those uncommitted files.

Relaunch service: `regrip-stage12-20261126-2.service`, runtime
`runtime/authorized_20261126_2/`. Remaining original budget is5sessions at
1800s each (2h30min child time), RuntimeMaxSec9180 with cleanup allowance.
This does not renew the original6session budget. Memory8GiB total/CPU200%/
Tasks256 and analysis-child4GiB/420s are unchanged. Actual live state is in
the new service and status.json; old service1 logs remain preserved.

The child retains workspace-write sandbox and submits an explicit per-cycle
save_request JSON. Only the separately authorized supervisor can save it.
It requires exact current HEAD, complete file list, SHA256, new result summaries,
no pre-existing untracked user work, no symlink/deletion/raw/oversize files,
no mutation of existing CAD/BOM/evidence, no manager/guard/criteria modification,
exact indexed bytes, unchanged trusted size guard and a normal local commit.
No arbitrary commands in manifests are executed. Missing/bad request stops
without cleanup. Never use this protocol to bypass another approval boundary.

Actual isolated tests: supervised_save_controls1 covers10 cases including two
real local saves. manager_flow1 runs the actual manager loop for two cycles
with a fake worker in a separate temporary Git repository: both saves commit
and continue, original untracked work remains, the launch budget stops at2,
and the actual gate call is read-only so it introduces no tracked dirt. No
Codex/account calls were made by these controls. These are software tests,
not Stage1/2 physics PASS. Research results remain subject to actual release.

New stop command:
`systemctl --user stop regrip-stage12-20261126-2.service`
The existing shared `runtime/STOP` file is still authoritative and persistent.

## Initial activation (historical)

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
