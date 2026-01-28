---
name: frontend-design-extractor
description: "Extract reusable UI/UX design systems from frontend codebases: design tokens, global styles, components, interaction patterns, and page templates. Use when analyzing any frontend repo (React/Vue/Angular/Next/Vite/etc.) to document or migrate UI/UX for reuse across projects. Focus on UI/UX only; explicitly ignore business logic and domain workflows."
---

# Frontend Design Extractor

## Overview
Extract a reusable UI/UX design spec from a frontend codebase by inventorying UI sources, documenting foundations, cataloging components, and capturing page-level patterns and behaviors. Exclude business logic and domain-specific workflows. Framework-agnostic: adapt to the actual stack in the target repo.

## Quick start
1) Confirm mode: new project (greenfield) or refactor existing. Clarify that business logic is out of scope.
2) If existing repo: run `scripts/scan_ui_sources.sh` to scan the repo root (no directory layout assumptions). It uses common globs + keyword hits, and ignores common build/cache dirs and extraction output folders by default.
3) Optionally: `scripts/scan_ui_sources.sh <repo_root> [out_file] [extra_glob ...]` or `--root/--out/--ignore` for nonstandard layouts.
4) Create the output folder (default `./ui-ux-spec`) via `scripts/generate_output_skeleton.sh` and write all extraction results inside it.
5) Produce outputs in the default structure (see "Output structure").

## Modes (choose one)

### A) Greenfield (from blank)
Goal: create a reusable UI/UX foundation and starter UI without business logic.

1) Define foundations: tokens (color/typography/spacing/radius/shadow/motion), global styles, breakpoints, layout shell.
2) Create a baseline component set: Button, Input, Select, Card, Modal, Table/List, Tabs, Toast, EmptyState.
3) Create page templates: list/detail/form/dashboard skeletons with placeholder data.
4) Provide implementation notes for the target framework (CSS architecture, theming mechanism, file structure).
5) Optionally run `scripts/generate_output_skeleton.sh [out_root]` to scaffold folders and empty templates. Default output root is `./ui-ux-spec`.

Deliverables:
- Design tokens doc + global styles spec
- Component catalog with variants/states/a11y
- Page templates with layout rules
- Engineering constraints (naming, CSS approach, theming)

### B) Refactor existing project
Goal: extract current UI/UX, normalize tokens, and plan safe, incremental improvements.

1) Inventory UI sources (scan script + manual inspection).
2) Normalize tokens and map existing styles to them.
3) Identify high-impact components/patterns for first pass.
4) Plan migration with minimal diffs (wrappers, theme adapters, gradual replacement).
5) Document behavioral and a11y gaps to fix progressively.

Deliverables:
- Extracted design spec (same as greenfield)
- Migration plan (phased, low-risk steps)
- Component-by-component mapping notes

## Refactor from spec (fixed flow)
Use this when applying an existing `ui-ux-spec/` to a target project. Always work from a plan and execute step-by-step to avoid missing gaps.

### 0) Understand the target project
- Identify framework, styling system, component library usage, and entry points.
- Confirm constraints: UI/UX only, business logic untouched.
- Keep existing project structure unchanged unless explicitly requested.

### 1) Build the refactor plan (required)
- Compare spec → current project and list differences by category:
  - Tokens & global styles
  - Components (priority order)
  - Patterns & pages
  - A11y gaps
- Do not assume the spec folder structure matches the target project. Map by content, not by paths.
- Produce a phased plan (Phase 1 tokens, Phase 2 base components, Phase 3 pages, etc.).
- Do not proceed to edits until the plan is accepted.

### 2) Execute phase by phase
- Apply changes for the current phase only.
- Re-check against the spec after each phase.
- Keep diffs minimal and reversible.
- Do not restructure folders or move files; update in place.

### 3) Summarize and verify
- Provide a change list and remaining gaps.
- Suggest next phase only after current phase is done.

## Refactor prompt templates
Use one of the templates below to keep requests precise and plan-driven.

### Template A: Standard refactor
```
Please refactor the existing project based on this UI/UX spec:
- Project path: /path/to/target-project
- Spec path: /path/to/ui-ux-spec
- Goal: UI/UX only (tokens, styles, components, layout), do not change business logic/APIs
- Scope: start with global styles + base components
- Constraints: minimal changes, small-step commits, reversible
- Deliverables: refactor plan + actual code changes + list of impacted files
```

### Template B: Phased refactor
```
Please refactor UI/UX in phases; only do Phase 1:
- Project path: /path/to/target-project
- Spec path: /path/to/ui-ux-spec
- Phase 1: align tokens + global styles (colors/typography/spacing/radius/shadows)
- Do not change: business logic/routing/APIs
- Deliverables: list of changed files + alignment diff notes
```

### Template C: Component-level refactor
```
Please align the following components to the spec while keeping business logic unchanged:
- Project path: /path/to/target-project
- Spec path: /path/to/ui-ux-spec
- Component list: Button, Input, Modal, Table
- Goal: only change styling/structure/interaction details
- Deliverables: alignment notes per component + code changes
```

## Workflow

### 0) Scope and constraints
- Confirm repo root, frameworks, and any design system packages.
- Confirm desired output format (Markdown by default).
- Ask for constraints: must-keep brand rules, target platforms, and accessibility level.
- Reconfirm: exclude business logic, business rules, and domain workflows.
- Do not assume a specific frontend framework or language; adapt to the project’s stack.

### 1) Source inventory (existing repos only)
- Do not assume a fixed directory structure; scan results should guide where to read.
- Run the scan script and inspect results for:
  - tokens/themes, global styles, theme providers
  - component libraries and local wrappers
  - Storybook, docs, or visual regression tests
  - assets and i18n sources

### 2) Foundations (tokens + global styles)
- Document colors, typography, spacing, radius, shadows, z-index, and motion tokens.
- Capture reset/normalize, body defaults, link/form defaults, focus-visible, scrollbar.

### 3) Layout & information architecture
- Document breakpoints, containers, grid rules, navigation structure, and layout shells.

### 4) Component catalog
- For each component, capture: purpose, structure/slots, variants, states, interactions, a11y, responsive behavior, motion, and theming hooks.
- If a third-party library is used, focus on local wrapper components and overrides.

### 5) Page templates & composition rules
- Extract page skeletons (list/detail/form/dashboard/etc.) and module ordering.
- Capture combined states: loading/empty/error/permission/readonly.

### 6) Behavior & content rules
- Capture loading and error strategies, validation patterns, undo/optimistic updates.
- Capture microcopy conventions and i18n formatting constraints.

### 7) Package outputs
- Produce at least:
  - Design tokens doc
  - Component catalog
  - Page templates
- Ensure outputs are written under a dedicated folder (default `ui-ux-spec/`).
- Use the output structure below unless the user asks for another layout.

## Output structure (default)
This structure is a recommended documentation layout. It does not need to match the target project's directory structure, and it can be renamed or relocated (e.g., `docs/ui-ux-spec/`).
```
ui-ux-spec/
  01_Foundation/
  02_Components/
  03_Patterns/
  04_Pages/
  05_A11y/
  06_Assets/
  07_Engineering_Constraints/
```

## Resources
- `scripts/scan_ui_sources.sh`: find candidate UI sources in a repo.
- `scripts/generate_output_skeleton.sh`: create the standard output folders and placeholder templates.
- `references/design-extraction-checklist.md`: detailed checklist derived from README.
