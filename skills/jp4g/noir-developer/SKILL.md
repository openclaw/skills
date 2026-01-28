---
name: noir-developer
description: Develop Noir (.nr) codebases. Use when creating a project or writing code with Noir.
---

# Noir Developer

## Workflow

1. Compile (`nargo compile`) Noir program into ACIR.
2. Generate witness (`nargo execute` or NoirJS execute) based on ACIR and user inputs.
3. Prove using ACIR and witness with the selected proving backend.
4. Verify proof with the selected proving backend.

## Task Patterns

### Environment

If the environment is unsupported by `nargo` (e.g. native Windows), guide the user to using GitHub Codespaces (https://noir-lang.org/docs/tooling/devcontainer#using-github-codespaces) or a supported setup (WSL, Docker, or VM).

### Plan

Define private inputs, public inputs (if any), and public outputs (if any) for each Noir program.

### Project Creation

When creating a Noir project, use `nargo new` or `nargo init` to scaffold it.

### Compilation

Use `nargo` (not `noir_wasm`) for compilation; it is the maintained path.

### Validation

Run `nargo test` to validate Noir implementations.

### Proving Backend

Confirm the proving backend choice before implementation details. If the user selects Barretenberg, read `references/barretenberg.md`.

## References

- Run `nargo --help` for the full list of commands.
- Read https://noir-lang.org/docs/ for language syntax, dependencies, and tooling.
- Proving backends:
  - For Barretenberg specifics, read `references/barretenberg.md`.
