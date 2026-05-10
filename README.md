# My Next Job Finder

An AI-assisted resume analyzer and tweaker built to help you land more interview calls.

Upload your resume (PDF or DOCX), optionally paste a target job description, and get:

- A structured **gap report**: ATS score, missing metrics, weak verbs, keyword overlap, timeline gaps
- **Bullet-level rewrite suggestions** you can accept, reject, or edit
- An **ATS-friendly DOCX export** of the polished resume

Future milestones add per-role tailoring, cover letters, an application tracker, and an **assisted-apply** flow that prepares each application but always leaves the final Submit click to you.

> **Design principle:** there is no fully-autonomous apply mode and there never will be. Every submission requires an explicit per-application user click in a real browser.

---

## Stack

| Layer    | Tech                                                     |
|----------|----------------------------------------------------------|
| Frontend | Vite + React + TypeScript + TailwindCSS + shadcn/ui      |
| Backend  | Python 3.11 + FastAPI + Pydantic v2 + SQLModel + SQLite  |
| LLM      | Anthropic Claude (`claude-sonnet-4-6`) with prompt caching |
| Tooling  | `uv` (Python), `pnpm` (Node), `ruff`, `mypy`, `eslint`, `prettier`, `pre-commit` |

---

## Prerequisites

- **Python 3.11**
- **Node 20** + **pnpm 9**
- **uv** (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- An **Anthropic API key**

---

## Quickstart

```bash
# 1. Clone
git clone <repo-url>
cd "My next job finder"

# 2. Backend env
cp backend/.env.example backend/.env
# edit backend/.env and set ANTHROPIC_API_KEY

# 3. Install everything + pre-commit hooks
make install

# 4. Run backend (:8000) and frontend (:5173) together
make dev
```

Open http://localhost:5173.

### Other useful commands

| Command          | What it does                                  |
|------------------|-----------------------------------------------|
| `make test`      | Run backend + frontend test suites            |
| `make lint`      | Run ruff, mypy, eslint, tsc                   |
| `make fmt`       | Format Python (ruff) and TS (prettier)        |
| `make precommit` | Run all pre-commit hooks against every file   |
| `make clean`     | Remove build artifacts and caches             |

---

## Project layout

```
.
├── backend/         FastAPI service
│   ├── app/         Application code
│   └── tests/
├── frontend/        Vite + React app
│   └── src/
├── .github/         CI workflows, templates, CODEOWNERS, dependabot
├── docs/            Architecture notes
└── Makefile
```

---

## Contributing

This is a multi-contributor project. Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening your first PR. The short version:

1. Fork or branch (`feat/...`, `fix/...`, `chore/...`).
2. Run `pre-commit install` once.
3. Write a test for any new behavior.
4. Open a PR — CI runs lint, type-check, and tests automatically. Branch protection requires green CI plus one approving review before merge.

---

## License

[MIT](LICENSE)
