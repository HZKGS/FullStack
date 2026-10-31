# FullStack

COM661 Full Stack Strategies and Development coursework workspace.

## Workspace Map

- `AGENT.md` - project-specific execution guide.
- `AGENTS.md` - Codex discovery entry point that points to the authoritative instructions.
- `AGENT_RULES.md` - mandatory agent behaviour and scope rules.
- `AGENT_RULE.md` - compatibility pointer to `AGENT_RULES.md`.
- `DECISIONS.md` - architecture and dataset decision log.
- `ERROR.md` - recurring-error prevention log.
- `NOTES.md` - progress and outstanding work.
- `WORKLOG.md` - dated implementation and verification diary.
- `指导书.md` - module/assignment guidance.
- `CW/` - coursework submission planning documents.
- `biz_bp/` - implemented Flask + MongoDB API project.
- `locallens-ui/` - Angular 22 frontend that displays live LocalLens business data.
- `run_locallens.ps1` - starts MongoDB, Flask and Angular, then prints the URLs.
- `stop_locallens.ps1` - stops the tracked API and UI processes.
- `.mongo/data/` - project-local MongoDB data directory.
- `.mongo/server/` - project-local MongoDB 9.0.4 server extracted from the provided MSI.
- `.runtime/` - local API/UI logs, PID files and verification screenshots, gitignored.

## One-command startup

```powershell
Set-Location 'G:\FullStack'
.\run_locallens.ps1 -OpenBrowser
```

Then use:

- Angular UI: `http://127.0.0.1:4200/`
- Flask API: `http://127.0.0.1:5000/`
- Raw business data: `http://127.0.0.1:5000/api/v1.0/businesses?pn=1&ps=5`

## Scope

All project files and generated artefacts must stay under `G:\FullStack`. Do not scan or use files from `C:\`.