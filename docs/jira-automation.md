# Jira Automation: firmware update flow

Build these rules in **RECORD → Project settings → Automation → Create rule** (needs project admin).
They replace the GitHub pipeline for ticket creation: Grafana and the device inventory are not
reachable from outside, so those steps stay manual inside Jira.

Facts about `RECORD` (read from Jira, 2026-11-12):
- Workflow for Task and Sub-task: `Open` → `In Progress` → `Closed`. `Closed` is the only done status.
- Required fields: Task needs summary + reporter; Sub-task needs summary + reporter + parent.
- Link types available: `Blocks`, `Depends on`, `Order Dependency`, `Relates`.

## Conventions
- **Release ticket:** a `Task` with label `firmware` and summary `Firmware <Vendor> <Model> <Version>`,
  for example `Firmware Epiphan Pearl-2 4.24.4`. Put the release-notes link in the description.
- **Device tasks** are Tasks with label `firmware-device` and must **never** carry the label
  `firmware`, otherwise Rule 1 fires on them.
- **Dedup key:** label `fw-<vendor>-<model>-<version>` in lowercase, for example
  `fw-epiphan-pearl-2-4.24.4`. This is the same key the Python pipeline uses.
- **Rule actor:** use a shared service account if possible, so tickets are not attributed to one person.
  Enable "Allow rule trigger" only where noted.

## Sub-task list (source of truth: `templates/subtasks.yaml`)
1. Review release notes and assess risk
2. Download firmware, verify checksum and archive
3. Test firmware in AV lab
4. Note relevant changes in the device model documentation page
5. Update Grafana dashboard baseline firmware
6. Create tasks for devices that need an update
7. Rollback plan
8. Communicate update schedule to stakeholders
9. Post-update verification and close-out

Each sub-task summary is `<name> – {{issue.summary}}`.

---

## Rule 1: Firmware release, create sub-tasks

| Setting | Value |
|---|---|
| Name | `Firmware: create sub-tasks` |
| Scope | Single project: RECORD |
| Trigger | **Issue created** |
| Condition 1 | **JQL**: `issuetype = Task AND labels = firmware` |

Steps:
1. **Create variable** `releaseKey` =
   `fw-{{issue.summary.replace("Firmware ","").toLowerCase().replace(" ","-")}}`
2. **Lookup issues**, JQL: `project = RECORD AND labels = "{{releaseKey}}"`
3. **Condition: Advanced compare**, first value `{{lookupIssues.size}}`, equals `0`
   - **If not met (duplicate):** Add comment `Duplicate of {{lookupIssues.first.key}}, not creating sub-tasks`,
     then **Transition issue** to `Closed`. Stop here.
4. **Edit issue**: add label `{{releaseKey}}`
5. **Create sub-tasks**: the 9 sub-tasks above (add each in the action; if the action cannot hold all
   of them, use nine **Create issue** actions with type `Sub-task` and parent = trigger issue).
6. **Add comment** on the trigger issue: `Created {{releaseKey}} checklist. Start with the lab test.`

The dedup lookup must run before the label is added (step 4), otherwise the issue matches itself.

## Device tasks: not a Jira rule

Device tasks are created from **Claude Code on a machine that can reach Grafana and the device
inventory**, because only there can we list the devices of a model that are below the new baseline.
There is no Jira rule for this. Contract for that workflow:
- Input: the release ticket key (e.g. `RECORD-123`).
- Gate: refuse to run unless the lab-test sub-task of that ticket is `Closed`.
- One Task per device, label `firmware-device` (never `firmware`), linked to the release ticket with
  `Relates`. Summary `<device>: <release ticket summary>`; description with current version, target version,
  location and maintenance window.
- Idempotent: skip devices that already have a `firmware-device` task linked to the release ticket.
- Rule 3b below closes the release ticket once these tasks are `Closed` too.

## Rule 3a: Lab test passed

| Setting | Value |
|---|---|
| Trigger | **Work item transitioned** to `Closed` |
| Condition | **JQL**: `issuetype = Sub-task AND summary ~ "Test firmware in AV lab"` |

Action: **Add comment** on the parent (use a **Branch rule / related issues → Parent**):
`Lab test passed. Next: document changes, update the Grafana baseline, then create the device tasks (Claude Code).`

## Rule 3b: Close the release when everything is done

| Setting | Value |
|---|---|
| Trigger | **Work item transitioned** to `Closed` |
| Condition 1 | **JQL**: `issuetype = Sub-task` |
| Condition 2 | **Advanced compare**: `{{issue.parent.labels}}` contains `firmware` |

Steps:
1. **Lookup issues**, JQL:
   `(parent = {{issue.parent.key}} OR (issue in linkedIssues({{issue.parent.key}}) AND labels = firmware-device)) AND status != Closed`
2. **Condition: Advanced compare**, `{{lookupIssues.size}}` equals `0`
3. Branch to **Parent**, **Transition issue** to `Closed`, and add comment `All sub-tasks and device tasks are closed.`

---

## Things to verify in the UI (not confirmed from here)
- `Labels` and `Description` are on the Task create screen. If not, Rule 1 step 4 still adds the label,
  but people creating tickets cannot set `firmware` on creation, so ask an admin to add it to the screen.
- `Open` → `Closed` is a direct transition (the duplicate branch and Rule 3b rely on it).
- The **Create sub-tasks** action accepts all 9 items.
- The smart value `{{issue.summary.replace("Firmware ","").toLowerCase().replace(" ","-")}}` renders as expected
  (check the audit log on the first run).
- Rule 3b's JQL with `linkedIssues()` is accepted in the lookup.
- Monthly automation run quota for your Atlassian plan.

## Test plan
1. Create a Task in RECORD with label `firmware`, summary `Firmware Test Dummy 0.0.0-test`.
2. Expect: label `fw-test-dummy-0.0.0-test` added, 9 sub-tasks created, one comment.
3. Create a second Task with the same summary. Expect: duplicate comment and `Closed`, no sub-tasks.
4. Close the lab-test sub-task. Expect the Rule 3a comment on the parent.
5. Create a dummy `firmware-device` Task linked to the parent (by hand or via Claude Code). Expect no
   sub-tasks on it (it must not trigger Rule 1).
6. Close all sub-tasks and the device task. Expect the parent to close.
7. Delete the test tickets.
