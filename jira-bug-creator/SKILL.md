---
name: jira-bug-creator
description: Create and verify K1 Jira (NK) bug reports from a short description and screenshots when the user asks to file an issue.
---

# K1 Jira Bug Creator

Use this skill only when the user asks to submit a Jira bug. A test finding or report entry alone does not authorize filing.

## Prepare

1. For a one sentence report with screenshots, follow [QA intake for K1](references/qa-intake-k1.md). Confirm reproducibility or label uncertainty. Record build, server, account, language, steps, expected and actual result, and evidence paths.
2. Use the `NK` Jira project. Select the current fix and affected versions from Jira; do not infer a version from an old report.
3. Check the requested assignee. If the user says “提给我”, use the user's Jira account. Do not replace an explicit assignee with a feature owner inferred by the script. Preserve an explicitly supplied `【功能名】` in the issue title.
4. Determine Jira priority separately from Bug level A–D. The JSON submission path requires both; inspect current Jira choices and ask when the evidence cannot support a priority.
5. Store your personal token in `~/.env.jira`, using `assets/jira.env.example` as a guide. Never commit a token or a filled `.env` file.

## Submit

Install `uv` or Python 3.10+ with `atlassian-python-api`, `python-dotenv`, and `requests`. Save one JSON object in a UTF-8 file outside this repository. See `assets/bug.example.json` for its shape. Review the file and attachment paths before submission.

```powershell
uv run --script <jira-bug-creator目录>/scripts/submit_from_json.py C:/path/to/bug.json
```

The command creates a Jira issue and uploads specified attachments. Do not run it as a dry run. For a local schema check without contacting Jira, add `--check`.

After creation, read back the issue key, project, summary, versions, assignee, Bug level, priority, reproduction steps and attachment list. Jira automation can change the assignee after creation, so check it again after a brief interval and report any difference. Include the Jira URL in the result.

## K1 filing rules

- Keep observed facts separate from suspected root causes. State exact steps and compare expected with actual behavior.
- Attach original screenshots/logs for defects. Redact credentials and personal data.
- Check Russian, Arabic and English UI where the finding concerns localization; specify the exact language in each issue.
- Use explicit `department`, `bug_level`, `priority`, `version`, `affect_version`, `assignee` and `reproduce_rate` when known. The creator's automatic guesses are fallbacks only.
- NK requires a fix version, affected version, label and reproduction steps. If any is unknown, inspect the issue or ask for the missing factual detail before creating it.
