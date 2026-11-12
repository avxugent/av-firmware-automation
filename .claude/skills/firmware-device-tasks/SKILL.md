---
name: firmware-device-tasks
description: Create one Jira task per AV device that needs a firmware update, for a given release ticket in RECORD. Use when asked to create device tasks for a firmware release (e.g. "create device tasks for RECORD-123"). Needs access to SAM (sam.ugent.be), so run it on a machine on the university network/VPN.
---

# Create device tasks for a firmware release

Context: the release ticket and its sub-tasks are created by Jira Automation (see
`docs/jira-automation.md`). Device tasks are created here because only this machine can reach SAM.

Input: the release ticket key, for example `RECORD-123`. If it is missing, ask for it.

Jira site: `universiteitgent.atlassian.net`, project `RECORD`. Use the Atlassian MCP tools
(`getJiraIssue`, `searchJiraIssuesUsingJql`, `createJiraIssue`, `createJiraIssueLink`).

## Steps

1. **Read the release ticket.** It must be a Task with label `firmware`. Its summary is
   `Firmware <Vendor> <Model> <Version>`; parse vendor, model and target version from it.
   Stop and report if the label or summary format does not match.

2. **Gate on the lab test.** List its sub-tasks. The one whose summary starts with
   `Test firmware in AV lab` must have status `Closed`. If not, stop and say so. Also
   mention (do not block on) whether the "Update Grafana dashboard baseline" sub-task is closed.

3. **Fetch devices from SAM.** <!-- TODO: fill in once the SAM API is known -->
   - Base URL: `https://sam.ugent.be`. Auth: token from the environment variable `SAM_API_TOKEN`.
     Never print the token, never write it to a file, never put it in a command that is logged.
   - Endpoint and query for "assets of model <Model>": **TO BE CONFIGURED** (ask the user for the
     SAM API documentation if this step has not been filled in).
   - Normalise each asset to a dict with at least: `name`, `model`, `firmware`, and, when
     available, `location`.

4. **Select devices below the target version.** Use the tested helper, do not compare versions by hand:
   ```bash
   PYTHONPATH=src python3 -c "
   import json, sys
   from fwwatch.devices import classify
   needs, unknown, current = classify(json.load(sys.stdin), '<Model>', '<Version>')
   print(json.dumps({'needs': needs, 'unknown': unknown, 'current': len(current)}, indent=2))
   " < devices.json
   ```
   Devices in `unknown` have no parseable firmware version: list them for the user, do not create tasks for them.

5. **Skip devices that already have a task.** Search with
   `labels = firmware-device AND issue in linkedIssues(<RELEASE-KEY>)` and skip any device whose name
   appears in an existing task summary.

6. **Show the plan and ask for confirmation.** Print the devices that will get a task (name, location,
   current version) and the skipped and unknown ones. Ask for the maintenance window (optional).
   Do not create anything before the user confirms.

7. **Create the tasks.** For each confirmed device:
   - `createJiraIssue`: project `RECORD`, type `Task`, labels `["firmware-device"]`,
     summary `<device name>: <release ticket summary>`, description with current version, target
     version, location and maintenance window.
   - `createJiraIssueLink`: type `Relates`, between the new task and the release ticket.
   - **Never** add the label `firmware` to a device task: it would trigger the sub-task rule.

8. **Report**: number of tasks created with their keys, plus skipped and unknown devices.

## Never
- Push firmware to devices, or change anything in SAM. This skill only reads SAM and writes Jira.
- Create tasks without the user's confirmation in step 6.
