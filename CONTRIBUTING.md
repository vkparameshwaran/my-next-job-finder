# Contributing

Thanks for working on My Next Job Finder. This guide covers everything you need to make a productive PR.

## Getting started

```bash
make install        # installs Python + Node deps and pre-commit hooks
cp backend/.env.example backend/.env  # add your ANTHROPIC_API_KEY
make dev            # runs backend (:8000) + frontend (:5173)
```

## Branching

- Trunk-based. Branch off `main`, merge back into `main`.
- Naming: `feat/<short-desc>`, `fix/<short-desc>`, `chore/<short-desc>`, `docs/...`, `test/...`, `refactor/...`.
- Keep branches short-lived. Rebase onto `main` before merging.

## Commits

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(parser): support multi-column PDF resumes
fix(api): return 422 on empty resume upload
chore(deps): bump anthropic to 0.40.0
```

Squash-merge is the default — your branch's commit messages don't need to be perfect, but the PR title does (it becomes the squashed commit).

## Pull requests

1. Open the PR against `main`.
2. Fill out the PR template (summary, motivation, screenshots if UI, test plan).
3. Wait for CI to pass:
   - `backend-ci` — ruff, mypy, pytest with 70% coverage gate
   - `frontend-ci` — eslint, tsc, vitest, build
   - `codeql` — security scan
4. Get one approving review.
5. Branch protection on `main` enforces all of the above; you cannot bypass.

## Test bar

Every PR that adds a public function or API route must add tests. The CI coverage gate is **70%** today and will be raised over time. Don't lower it.

### Running tests

```bash
make test                                 # everything
cd backend && uv run pytest -k parser    # backend, focused
cd frontend && pnpm test --watch          # frontend, watch mode
```

### LLM in tests

Never call the real Anthropic API in tests. The `anthropic.Anthropic` client is dependency-injected through `backend/app/core/config.py`. In tests, use the `fake_anthropic_client` fixture from `backend/tests/conftest.py`, which serves canned JSON responses from `backend/tests/fixtures/llm_responses/`. To test against a new LLM behavior, capture a real response once and check it in.

## Code style

- **Python**: `ruff` for lint + format, `mypy --strict` on `app/`. Line length 100.
- **TypeScript**: `eslint` + `prettier`. `tsconfig` is strict (`strict: true`, `noUncheckedIndexedAccess: true`).
- **Comments**: only when the *why* is non-obvious. No commentary on what well-named code already says.
- **Docstrings**: only on public functions where the contract isn't obvious from the signature.

`pre-commit install` runs all of this automatically before each commit.

## Adding a new feature

A few common extension points:

- **A new analyzer rule** → `backend/app/analyzer/`. Follow the pattern in `gap_finder.py`. Add unit tests with the fake LLM client.
- **A new resume parser** (e.g. RTF) → `backend/app/parsers/`. Implement the same interface as `pdf_parser.py`. Wire it up in `app/api/resume.py`.
- **A new frontend page** → `frontend/src/pages/`, register the route in `App.tsx`, add a vitest in `frontend/src/__tests__/`.

## Security

- Never commit secrets. `.env` is gitignored; use `.env.example` for placeholders.
- The `detect-private-key` pre-commit hook will reject obvious key material.
- Found a security issue? Email the maintainers privately rather than filing a public issue.

## Reporting bugs / requesting features

Use the issue templates in `.github/ISSUE_TEMPLATE/`. The bug template asks for repro steps; the feature template asks for the user problem (not the proposed solution).
