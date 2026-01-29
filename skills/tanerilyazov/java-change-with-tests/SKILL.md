# java-change-with-tests

## When to use
- Any Java change that must be merged safely (feature/refactor/bugfix).

## Inputs to request (if missing)
- Acceptance criteria (1-3 bullets).
- Module name (if multi-module repo).
- Build tool and test conventions.
- Whether integration tests are required for the change.

## Steps
1. Repo map (brief): identify the module, entrypoint, and test location.
2. Plan: smallest diff that meets acceptance criteria.
3. Implement: minimal edits.
4. Tests:
   - prefer fast unit tests first
   - add integration tests only when required to validate behavior
5. Verify:
   - run targeted tests
   - run `mvn -q test` (or module-scoped equivalent)
6. Output PR-ready summary with evidence.

## Verification commands (project-specific)
- Use the repo's build tool and record the exact commands and results.
- Prefer targeted unit tests before full test suites.

## Output contract
1) Plan (3-6 steps)
2) Files changed + intent
3) Commands run + results
4) Risks + follow-ups
