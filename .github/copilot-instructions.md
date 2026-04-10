# Testing Enforcement Rules — Todo-Crud

## TDD Workflow (Non-Negotiable)
1. Write the test FIRST — see it fail (Red)
2. Write minimal code to pass — see it pass (Green)
3. Refactor — tests still pass (Refactor)

## Testing Pyramid
- Pure Unit Tests: No I/O, no framework imports, stub injection only
- Integration Tests: Framework mocking allowed, real orchestration
- Behavioral Tests: Detector perception — "Does it SEE the files?"
- Adapter Tests: Real I/O in temp directories, no mocks

## Mock Tax Rule
If test file LOC > 2x source file LOC:
- DELETE the unit test
- Write an integration test instead
- Never try to "fix" or "reduce" the unit test

## Pre-commit Hooks (17 hooks active)
- NEVER use --no-verify to skip hooks
- Wait for hooks to pass before declaring work complete
- Fix failures, do not bypass them

## Test Runners
- Backend (Python): `cd backend && pytest`
- Frontend (TypeScript): `cd frontend && npx vitest run`
- TIA (changed files only): `make test-tia`

## Test Location
- Backend unit tests: `backend/tests/unit/test_*.py`
- Backend integration tests: `backend/tests/integration/test_*.py`
- Frontend tests: `frontend/src/*.test.ts`
- Shared fixtures: `backend/tests/conftest.py`

## Coverage
- Backend: `pytest --cov --cov-fail-under=80` (currently 100%)
- Frontend: `vitest --coverage` (currently 100% on api.ts)
- Per-file ratchet: coverage cannot regress below baseline

## Before Every Change
1. Check if tests exist for the file being modified
2. If no tests exist, write them FIRST
3. Run the full test suite before declaring complete

## Governance Gates (enforced at commit time + CI)
- Silent catch ratchet: no empty except/catch blocks
- Type hole ratchet: no new `# type: ignore` or `as any`
- Lint suppression ratchet: no new `# noqa` or `eslint-disable`
- Mock tax: mocked test LOC ≤ 2x source LOC
- SRP guardrails: files ≤ 600 LOC, functions ≤ 50 LOC
- Skipped test gate: < 5% tests skipped

## Branch Protocol
- Always create `feat/`/`fix/`/`chore/`/... branches (never push to main)
- PR titles must follow conventional commits (`feat:` / `fix:` / `chore:` / etc.)
- 6 required CI checks must pass before merge
